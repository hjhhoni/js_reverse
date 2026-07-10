# -*- coding: utf-8 -*-
"""
HiredChina.com 电子信息工程岗位采集（纯协议）
目标：https://www.hiredchina.com/en/jobs
范围：5 国（新加坡/马来西亚/菲律宾/越南/泰国）× 电子信息工程相关岗位
接口：GET /api/v2/jobs?page=&limit=&where={"nationId":N}  （明文 JSON，无签名/无加密）

用法：
    python main.py                 # 全量采集 5 国，输出 data/jobs.csv 与 data/jobs.json
    python main.py --country 152   # 仅采集新加坡
    python main.py --test          # 每国仅取首页，快速验证
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import logging

# Windows 控制台 UTF-8，避免中文日志乱码
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import requests

import config as C
import filter_electronics as F

# ------------------------------------------------------------
# 日志
# ------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("hiredchina")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

# ------------------------------------------------------------
# HTTP（带重试，对 Cloudflare 友好）
# ------------------------------------------------------------
SESSION = requests.Session()
SESSION.cookies.update(C.COOKIES)
SESSION.headers.update(C.HEADERS)


def fetch_page(nation_id, page, limit=C.PAGE_SIZE, timeout=30):
    """拉取单页岗位列表。返回 list（可能为空）。Cloudflare 偶发 TLS 重置 -> 指数退避重试。"""
    where = C.build_where({"nationId": nation_id})
    url = f"{C.LIST_API}?page={page}&limit={limit}&where={where}"
    last_err = None
    for attempt in range(1, C.MAX_RETRIES + 1):
        try:
            resp = SESSION.get(url, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    return data.get("data", {}).get("list", []) or []
                log.warning("非零业务码: %s", data)
                return []
            last_err = f"HTTP {resp.status_code}"
        except requests.RequestException as e:
            last_err = str(e)[:120]
        # 指数退避：2,4,8,16,20,20（Cloudflare TLS 重置通常几秒内恢复）
        backoff = min(C.RETRY_BACKOFF_BASE * (2 ** (attempt - 1)), 20)
        log.warning("[%s] 第%d页 %s，%ds 后 %d/%d 重试", nation_id, page, last_err, backoff, attempt, C.MAX_RETRIES)
        time.sleep(backoff)
    log.error("[%s] 第%d页最终失败: %s", nation_id, page, last_err)
    return None  # None 表示彻底失败（区别于空页 []）


def fetch_count(nation_id):
    """取该国岗位总数（API count 字段）。"""
    where = C.build_where({"nationId": nation_id})
    url = f"{C.LIST_API}?page=1&limit=1&where={where}"
    try:
        data = SESSION.get(url, timeout=30).json()
        return data.get("data", {}).get("count", 0)
    except Exception:
        return 0


def fetch_country(nation_id, country_name, test=False):
    """拉取某国全部岗位，以 API count 校验完整性。返回 list。"""
    log.info("▶ 采集 %s(id=%s) ...", country_name, nation_id)
    expected = fetch_count(nation_id)
    log.info("  API count = %d", expected)

    first = fetch_page(nation_id, 1)
    if first is None:
        log.error("  首页彻底失败，跳过该国")
        return []
    all_jobs = list(first)
    if test:
        return all_jobs

    seen = {j.get("id") for j in all_jobs}
    import math
    total_pages = math.ceil(expected / C.PAGE_SIZE) if expected else 999
    page = 2
    failed_pages = []
    while page <= total_pages:
        time.sleep(C.REQUEST_DELAY)
        batch = fetch_page(nation_id, page)
        if batch is None:
            failed_pages.append(page)           # 彻底失败，记录但不中断
        elif batch:
            for j in batch:
                if j.get("id") not in seen:
                    all_jobs.append(j)
                    seen.add(j.get("id"))
        else:
            break                                # 真空页，结束
        if len(all_jobs) >= expected and expected:
            break
        page += 1

    # 失败页补采一轮
    if failed_pages:
        log.warning("  %d 页失败，补采：%s", len(failed_pages), failed_pages)
        for p in failed_pages:
            time.sleep(2)
            batch = fetch_page(nation_id, p)
            if batch:
                for j in batch:
                    if j.get("id") not in seen:
                        all_jobs.append(j)
                        seen.add(j.get("id"))

    gap = expected - len(all_jobs)
    flag = "✔" if gap <= 0 else f"⚠ 缺 {gap}"
    log.info("%s %s 采集 %d 条（API count=%d）%s", flag, country_name, len(all_jobs), expected,
             "" if gap <= 0 else f"，缺失 {gap}")
    return all_jobs


# ------------------------------------------------------------
# 字段映射：原始 job -> 14 字段交付结构
# ------------------------------------------------------------
def extract_education(desc):
    """站点 qualificationKey 全站为空；从描述轻量识别学历（面向本科及以上）。"""
    if not desc:
        return ""
    low = desc.lower()
    if re.search(r"ph\.?d|doctorate", low):
        return "PhD and above"
    if re.search(r"master|postgraduate|m\.?sc|mba", low):
        return "Master and above"
    if re.search(r"bachelor|undergraduate|degree|b\.?sc|b\.?eng", low):
        return "Bachelor and above"
    return ""


def build_record(job):
    """按《爬虫说明.md》14 字段映射。"""
    title = (job.get("title") or "").strip()
    company_name = (job.get("companyName") or "").strip()
    desc = (job.get("description") or "").strip()

    # 经验要求
    exp = C.EXP_MAP.get(job.get("workingYearsKey"), "")

    # 学历要求：站点 qualificationKey 全站为空 -> 从描述识别（面向本科及以上）
    edu = extract_education(desc)

    # 工作地点：优先 overseasArea（站点真实城市/地址，5 国约 25% 有值），
    # 国家名作前缀；overseasArea 为空才回退到国家名。
    # （注：areas 字段对 5 国岗位基本只有 overseas/others，不采用）
    nation = C.NATION_MAP.get(job.get("nationKey"), "")
    ov = (job.get("overseasArea") or "").strip()
    if ov:
        location = f"{nation} · {ov}" if nation else ov
    else:
        location = nation

    # 薪资待遇（必须为数据）：salaryKey -> 数值范围（RMB/月）
    salary_range = C.SALARY_MAP.get(job.get("salaryKey"), "")
    salary = salary_range if salary_range else ""

    # 公司行业
    industry = C.INDUSTRY_MAP.get((job.get("company") or {}).get("industryKey"), "")

    # 招聘状态
    state_key = job.get("stateTypeKey")
    if job.get("isStop") == 1 and state_key != "support.statetype.approved":
        state = "Closed"
    else:
        state = C.STATE_MAP.get(state_key, state_key or "")

    # 企业类型 / 企业规模 / 企业介绍：站点 RSC 仅有 {name,industry,website,logo}，
    # 无结构化规模/类型/介绍 -> 按规则「没有就没有」留空
    company_type = ""
    company_scale = ""
    company_intro = ""

    # 原始 URL
    line = job.get("line") or ""
    url = C.JOB_URL_TPL.format(line=line) if line else ""

    # 招聘人数：站点无此字段 -> 按规则默认 1
    headcount = 1

    return {
        "招聘岗位名称": title,
        "招聘人数": headcount,
        "经验要求": exp,
        "学历要求": edu,
        "企业名称": company_name,
        "企业类型": company_type,
        "工作地点": location,
        "薪资待遇(RMB/月)": salary,
        "公司行业": industry,
        "企业规模": company_scale,
        "企业介绍": company_intro,
        "岗位描述": desc,
        "招聘状态": state,
        "原始URL": url,
    }


# ------------------------------------------------------------
# 输出
# ------------------------------------------------------------
FIELDNAMES = [
    "招聘岗位名称", "招聘人数", "经验要求", "学历要求", "企业名称", "企业类型",
    "工作地点", "薪资待遇(RMB/月)", "公司行业", "企业规模", "企业介绍",
    "岗位描述", "招聘状态", "原始URL", "匹配关键词",
]


def write_csv(records, path):
    # extrasaction='ignore'：记录里若有 _匹配原因 等调试字段，不计入正式 14 字段
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        w.writeheader()
        for r in records:
            w.writerow(r)
    log.info("CSV 已写出: %s（%d 条）", path, len(records))


def write_json(records, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    log.info("JSON 已写出: %s（%d 条）", path, len(records))


# ------------------------------------------------------------
# 主流程
# ------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", type=int, help="仅采集指定 nationId")
    ap.add_argument("--test", action="store_true", help="每国仅取首页（快速验证）")
    ap.add_argument("--no-filter", action="store_true", help="不过滤，导出全量岗位（调试）")
    args = ap.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)

    countries = {args.country: C.COUNTRIES[args.country]} if args.country else C.COUNTRIES

    # ---- 采集全部原始岗位 ----
    raw_jobs = []
    for nid, name in countries.items():
        jobs = fetch_country(nid, name, test=args.test)
        log.info("  %s: 采集 %d 条", name, len(jobs))
        raw_jobs.extend(jobs)
    log.info("原始岗位合计：%d", len(raw_jobs))

    # ---- --no-filter：导出全量 ----
    if args.no_filter:
        recs = [build_record(j) for j in raw_jobs]
        write_csv(recs, os.path.join(DATA_DIR, "jobs_all.csv"))
        write_json(recs, os.path.join(DATA_DIR, "jobs_all.json"))
        log.info("完成（全量 %d 条，未过滤）。", len(recs))
        return

    # ---- 强电子词匹配（标题或描述命中即纳入）----
    recs = []
    for j in raw_jobs:
        ok, reason = F.is_electronic(j)
        if ok:
            rec = build_record(j)
            rec["匹配关键词"] = reason
            rec["_匹配原因"] = reason
            recs.append(rec)
    # 标题命中的排前面，其次描述命中
    recs.sort(key=lambda r: 0 if r["匹配关键词"].startswith("标题") else 1)

    ts = time.strftime("%Y%m%d_%H%M%S")
    suffix = "" if args.test else f"_{ts}"
    write_csv(recs, os.path.join(DATA_DIR, f"jobs_electronic{suffix}.csv"))
    write_json(recs, os.path.join(DATA_DIR, f"jobs_electronic{suffix}.json"))
    if not args.test:
        write_csv(recs, os.path.join(DATA_DIR, "jobs_latest.csv"))
        write_json(recs, os.path.join(DATA_DIR, "jobs_latest.json"))
    title_hit = sum(1 for r in recs if r["匹配关键词"].startswith("标题"))
    desc_hit = len(recs) - title_hit
    log.info("硬核电子岗: %d 条（标题命中 %d + 描述命中 %d）-> jobs_latest + jobs_electronic%s",
             len(recs), title_hit, desc_hit, suffix)
    log.info("完成。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("用户中断")
        sys.exit(130)
