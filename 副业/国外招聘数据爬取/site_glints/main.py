# -*- coding: utf-8 -*-
"""
Glints 电子信息工程岗位采集（纯协议）
SERP: POST /api/v2-alc/graphql searchJobsV3，按 CountryCode 拉 5 国全量，本地电子过滤
详情: GET /{cc}/opportunities/jobs/{slug}/{id}（SSR 无 Turnstile），解析补岗位描述/企业规模/介绍
反爬: curl_cffi chrome 指纹 + 代理换IP + 间隔（参照 jobstreet 教训）

用法:
  python main.py              # 5 国全量 + 电子过滤 + 详情
  python main.py --country SG # 仅一国
  python main.py --max-pages 3 # 限制每国页数（调试）
  python main.py --no-detail  # 不抓详情（调试，描述留空）
"""
import argparse, csv, json, os, re, sys, time, logging, html as htmllib
try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass
from curl_cffi import requests
import config as C
from filter import is_electronic

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("glints")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

SESSION = (requests.Session(impersonate="chrome", proxies={"http": C.PROXY, "https": C.PROXY})
           if C.PROXY else requests.Session(impersonate="chrome"))

# educationLevel -> 可读
EDU_MAP = {
    "HIGH_SCHOOL": "High School", "VOCATIONAL_HIGH_SCHOOL": "Vocational High School",
    "SENIOR_HIGH_SCHOOL": "Senior High School", "DIPLOMA": "Diploma",
    "ASSOCIATE_DEGREE": "Associate Degree", "BACHELOR_DEGREE": "Bachelor",
    "BACHELOR": "Bachelor", "MASTER_DEGREE": "Master", "MASTER": "Master",
    "DOCTORATE": "PhD", "NOT_REQUIRED": "Not required", "ANY": "",
}


def fetch_search(cc, page):
    """searchJobsV3 单页。返回 (jobs[], hasMore)。"""
    payload = {"operationName": "searchJobsV3",
               "variables": {"data": {"CountryCode": cc, "includeExternalJobs": False,
                                       "pageSize": C.PAGE_SIZE, "page": page}},
               "query": C.SEARCH_QUERY}
    last = None
    for attempt in range(1, C.MAX_RETRIES + 1):
        try:
            r = SESSION.post(C.GQL + "?op=searchJobsV3", headers=C.HEADERS, json=payload, timeout=30)
            if r.status_code == 200:
                j = r.json()
                if j.get("errors"):
                    log.warning("gql err: %s", j["errors"][0].get("message", "")[:100])
                    return [], False
                d = (j.get("data") or {}).get("searchJobsV3") or {}
                return d.get("jobsInPage") or [], bool(d.get("hasMore"))
            last = f"HTTP {r.status_code}"
            if r.status_code in (403, 429):
                log.warning("[%s] 第%d页 限流%s，冷却%ds", cc, page, last, C.LIMIT_COOLDOWN)
                time.sleep(C.LIMIT_COOLDOWN); continue
        except Exception as e:
            last = str(e)[:100]
        time.sleep(min(2 ** attempt, 20))
    log.error("[%s] 第%d页最终失败: %s", cc, page, last)
    return [], False


def collect_country(cc, name, max_pages=None):
    log.info("▶ %s(%s)", name, cc)
    jobs, page, seen = [], 1, set()
    while True:
        batch, has_more = fetch_search(cc, page)
        if not batch:
            break
        n0 = len(seen)
        for j in batch:
            if j["id"] not in seen:
                seen.add(j["id"]); jobs.append(j)
        log.info("  第%d页 %d 条（累计 %d）", page, len(batch), len(jobs))
        if not has_more or (max_pages and page >= max_pages):
            break
        if len(seen) == n0:
            break
        page += 1; time.sleep(C.REQUEST_DELAY)
    log.info("✔ %s 共 %d 条", name, len(jobs))
    return jobs


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")
    return s or "job"


def _clean_text(html):
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = htmllib.unescape(t)
    t = re.sub(r"\n{2,}", "\n", t).strip()
    return t


def parse_detail(html_text):
    """从详情 SSR HTML 提取 岗位描述/企业规模/企业介绍/学历。"""
    t = _clean_text(html_text)
    # 岗位描述：'Job description for ...' 到 'About the company'
    desc = ""
    m = re.search(r"Job description for .*?\n(.+?)(?:\nAbout the company|$)", t, re.S)
    if m:
        desc = m.group(1).strip()
    # 企业规模
    scale = ""
    m = re.search(r"([\d,]+\s*[-–]\s*[\d,]+\s*employees|[\d,]+\+\s*employees|\d+\s*employees)", t)
    if m:
        scale = m.group(1).strip()
    # 企业介绍：'About the company\n{名}\n{行业}\n{规模}\n\n{介绍}' 到 'Read More'/'Office address'
    intro = ""
    m = re.search(r"About the company\n.*?\n.*?\n[^\n]*employees\n(.+?)(?:\nRead More|\nOffice address|\nCompany gallery|$)", t, re.S)
    if m:
        intro = re.sub(r"\n{2,}", "\n", m.group(1)).strip()
    # 学历（详情 "Minimum ..." 更完整）
    edu = ""
    m = re.search(r"(Minimum\s+[\w\s/]*(?:School|Degree|Diploma|Bachelor|Master|PhD)[\w\s/]*)", t)
    if m:
        edu = re.sub(r"\s+", " ", m.group(1)).strip()
    return desc, scale, intro, edu


def fetch_detail(cc, job):
    url = C.DETAIL_URL.format(cc=cc.lower(), slug=slugify(job.get("title")), job_id=job["id"])
    for attempt in range(1, C.MAX_RETRIES + 1):
        try:
            r = SESSION.get(url, headers={k: v for k, v in C.HEADERS.items() if k != "Content-Type"}, timeout=30)
            if r.status_code == 200:
                return parse_detail(r.text)
            if r.status_code in (403, 429):
                time.sleep(C.LIMIT_COOLDOWN); continue
            log.warning("  详情 %s HTTP %s", job["id"][:8], r.status_code)
            break
        except Exception as e:
            log.warning("  详情异常 %s", str(e)[:80])
        time.sleep(min(2 ** attempt, 16))
    return "", "", "", ""


def fmt_salary(job):
    sals = job.get("salaries") or []
    if not sals:
        return ""
    s = sals[0]
    lo, hi, cur = s.get("minAmount"), s.get("maxAmount"), s.get("CurrencyCode") or ""
    if lo is None and hi is None:
        return ""
    return f"{lo or ''}-{hi or ''} {cur}".strip()


def fmt_exp(job):
    lo, hi = job.get("minYearsOfExperience"), job.get("maxYearsOfExperience")
    if lo is None and hi is None:
        return ""
    if lo == 0 and hi and hi >= 50:
        return "Unlimited"
    return f"{lo or 0}-{hi or ''} years".replace("- years", "+ years")


def build_record(cc, job, detail):
    desc, scale, intro, edu_d = detail
    edu = edu_d or EDU_MAP.get(job.get("educationLevel"), job.get("educationLevel") or "")
    loc_parts = []
    if job.get("city") and job["city"].get("name"): loc_parts.append(job["city"]["name"])
    if job.get("location") and job["location"].get("formattedName"): loc_parts.append(job["location"]["formattedName"])
    comp = (job.get("company") or {}).get("name") or ""
    ind = ((job.get("company") or {}).get("industry") or {}).get("name") or ""
    status = "Recruiting" if job.get("status") == "OPEN" else (job.get("status") or "")
    url = C.DETAIL_URL.format(cc=cc.lower(), slug=slugify(job.get("title")), job_id=job["id"])
    return {
        "招聘岗位名称": (job.get("title") or "").strip(),
        "招聘人数": 1,
        "经验要求": fmt_exp(job),
        "学历要求": edu,
        "企业名称": comp,
        "企业类型": "",
        "工作地点": " / ".join(loc_parts),
        "薪资待遇": fmt_salary(job),
        "公司行业": ind,
        "企业规模": scale,
        "企业介绍": intro,
        "岗位描述": desc,
        "招聘状态": status,
        "原始URL": url,
    }


FIELDNAMES = ["招聘岗位名称", "招聘人数", "经验要求", "学历要求", "企业名称", "企业类型",
              "工作地点", "薪资待遇", "公司行业", "企业规模", "企业介绍",
              "岗位描述", "招聘状态", "原始URL"]


def write_csv(records, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        w.writeheader()
        for r in records:
            w.writerow(r)
    log.info("CSV: %s (%d)", os.path.basename(path), len(records))


def write_json(records, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    log.info("JSON: %s (%d)", os.path.basename(path), len(records))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", choices=list(C.COUNTRIES))
    ap.add_argument("--max-pages", type=int, default=None)
    ap.add_argument("--no-detail", action="store_true")
    args = ap.parse_args()
    os.makedirs(DATA_DIR, exist_ok=True)
    countries = {args.country: C.COUNTRIES[args.country]} if args.country else C.COUNTRIES

    all_records = []
    for cc, name in countries.items():
        jobs = collect_country(cc, name, args.max_pages)
        kept = [j for j in jobs if is_electronic(j)[0]]
        log.info("  %s: 原始 %d -> 电子 %d", name, len(jobs), len(kept))
        for j in kept:
            detail = ("", "", "", "") if args.no_detail else fetch_detail(cc, j)
            time.sleep(C.DETAIL_DELAY)
            all_records.append(build_record(cc, j, detail))
    ts = time.strftime("%Y%m%d_%H%M%S")
    write_csv(all_records, os.path.join(DATA_DIR, f"jobs_{ts}.csv"))
    write_json(all_records, os.path.join(DATA_DIR, f"jobs_{ts}.json"))
    write_csv(all_records, os.path.join(DATA_DIR, "jobs_latest.csv"))
    write_json(all_records, os.path.join(DATA_DIR, "jobs_latest.json"))
    log.info("完成。合计 %d 条。", len(all_records))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("中断"); sys.exit(130)
