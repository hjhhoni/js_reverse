# -*- coding: utf-8 -*-
"""
Glints 电子信息工程岗位采集（纯协议 GET + __NEXT_DATA__）
机制：GET 关键词搜索页 -> __NEXT_DATA__ JSON -> jobsInPage（标准 JSON）
      详情 GET -> __NEXT_DATA__ 补岗位描述/企业规模/介绍
反爬：curl_cffi chrome 指纹 + 代理换 IP + 间隔

用法:
  python main.py                # 5国 × 电子关键词
  python main.py --country SG   # 单国
  python main.py --kw "hardware engineer"  # 单关键词
"""
import argparse, csv, json, os, re, sys, time, logging
from urllib.parse import quote
try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass
from curl_cffi import requests
import config as C

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("glints")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
SESSION = (requests.Session(impersonate="chrome", proxies={"http": C.PROXY, "https": C.PROXY})
           if C.PROXY else requests.Session(impersonate="chrome"))

EDU_MAP = {
    "HIGH_SCHOOL": "High School", "VOCATIONAL_HIGH_SCHOOL": "Vocational High School",
    "SENIOR_HIGH_SCHOOL": "Senior High School", "DIPLOMA": "Diploma",
    "ASSOCIATE_DEGREE": "Associate Degree", "BACHELOR_DEGREE": "Bachelor",
    "BACHELOR": "Bachelor", "MASTER_DEGREE": "Master", "MASTER": "Master",
    "DOCTORATE": "PhD", "NOT_REQUIRED": "", "ANY": "",
}
SIZE_MAP = {
    "LESS_THAN_10": "<10", "BETWEEN_11_AND_50": "11-50",
    "BETWEEN_51_AND_200": "51-200", "BETWEEN_201_AND_500": "201-500",
    "BETWEEN_501_AND_1000": "501-1000", "BETWEEN_1001_AND_5000": "1001-5000",
    "MORE_THAN_5000": "5000+",
}


def parse_next_data(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def _get(obj, *keys, default=None):
    for k in keys:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(k)
        if obj is None:
            return default
    return obj


def fetch_url(url):
    """GET + 重试，返回 text 或 ''。"""
    last = None
    for attempt in range(1, C.MAX_RETRIES + 1):
        try:
            r = SESSION.get(url, headers=C.HEADERS, timeout=30)
            if r.status_code == 200:
                return r.text
            last = f"HTTP {r.status_code}"
            if r.status_code in (403, 429):
                log.warning("  限流 %s，冷却%ds（%d/%d）", last, C.LIMIT_COOLDOWN, attempt, C.MAX_RETRIES)
                time.sleep(C.LIMIT_COOLDOWN); continue
        except Exception as e:
            last = str(e)[:80]
        time.sleep(min(2 ** attempt, 16))
    log.error("  最终失败 %s: %s", url.split('?')[0], last)
    return ""


def fetch_search(cc, kw, page):
    """关键词搜索一页，返回 (jobs[], hasMore)。"""
    url = C.SEARCH_URL.format(ccl=cc.lower(), cc=cc, kw=quote(kw), page=page)
    html = fetch_url(url)
    if not html:
        return [], False
    nd = parse_next_data(html)
    ij = _get(nd, "props", "pageProps", "initialJobs", default={}) or {}
    return ij.get("jobsInPage") or [], bool(ij.get("hasMore"))


def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-") or "job"


def extract_richtext(s):
    """glints descriptionJsonString 是 Draft.js 富文本（{blocks:[{text:...}]}），提纯文本。"""
    if not s:
        return ""
    try:
        obj = json.loads(s) if isinstance(s, str) else s
    except Exception:
        return str(s)
    if isinstance(obj, dict) and isinstance(obj.get("blocks"), list):
        return "\n".join(b.get("text", "") for b in obj["blocks"] if isinstance(b, dict)).strip()
    texts = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("type") == "text" and isinstance(o.get("text"), str):
                texts.append(o["text"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return "\n".join(texts).strip() or str(s)


def fetch_detail(cc, job):
    """GET 详情 -> __NEXT_DATA__ -> 岗位描述/企业规模/企业介绍。"""
    url = C.DETAIL_URL.format(ccl=cc.lower(), slug=slugify(job.get("title")), job_id=job["id"])
    html = fetch_url(url)
    if not html:
        return "", "", ""
    nd = parse_next_data(html)
    pp = _get(nd, "props", "pageProps", default={}) or {}
    dj = _get(pp, "initialData", "data", default={}) or {}
    if not dj:  # 兜底：遍历 pageProps 找含 descriptionJsonString 的对象
        for v in pp.values():
            if isinstance(v, dict) and v.get("descriptionJsonString"):
                dj = v; break
    desc = extract_richtext(dj.get("descriptionJsonString"))
    comp = dj.get("company") or {}
    scale = SIZE_MAP.get(comp.get("size"), comp.get("size") or "")
    intro = extract_richtext(comp.get("descriptionJsonString"))
    return desc, str(scale), intro


def fmt_salary(job):
    sals = job.get("salaries") or []
    if not sals:
        return "保密"
    s = sals[0]
    lo, hi, cur = s.get("minAmount"), s.get("maxAmount"), s.get("CurrencyCode") or ""
    if lo is None and hi is None:
        return "保密"
    # glints 薪资上限占位（19999-20000 之类）当保密
    if (hi and hi >= 19999) or (lo and lo >= 19999):
        return "保密"
    if lo == hi:
        return f"{lo} {cur}".strip()
    return f"{lo if lo is not None else ''}-{hi if hi is not None else ''} {cur}".strip()


def fmt_exp(job):
    lo, hi = job.get("minYearsOfExperience"), job.get("maxYearsOfExperience")
    if lo is None and hi is None:
        return ""
    if (lo == 0 or lo is None) and hi and hi >= 50:
        return "Unlimited"
    return f"{lo or 0}-{hi or ''} years".replace("- years", "+ years")


def build_record(cc, job, detail):
    desc, scale, intro = detail
    comp = job.get("company") or {}
    loc = []
    city = (job.get("city") or {}).get("name")
    floc = (_get(job, "location", "formattedName"))
    if city: loc.append(city)
    if floc: loc.append(floc)
    return {
        "招聘岗位名称": (job.get("title") or "").strip(),
        "招聘人数": 1,
        "经验要求": fmt_exp(job),
        "学历要求": EDU_MAP.get(job.get("educationLevel"), job.get("educationLevel") or ""),
        "企业名称": (comp.get("name") or "").strip(),
        "企业类型": "",
        "工作地点": " / ".join(loc),
        "薪资待遇": fmt_salary(job),
        "公司行业": ((comp.get("industry") or {}).get("name") or "").strip(),
        "企业规模": scale,
        "企业介绍": intro,
        "岗位描述": desc,
        "招聘状态": "Recruiting" if job.get("status") == "OPEN" else (job.get("status") or ""),
        "原始URL": C.DETAIL_URL.format(ccl=cc.lower(), slug=slugify(job.get("title")), job_id=job["id"]),
    }


FIELDNAMES = ["招聘岗位名称", "招聘人数", "经验要求", "学历要求", "企业名称", "企业类型",
              "工作地点", "薪资待遇", "公司行业", "企业规模", "企业介绍",
              "岗位描述", "招聘状态", "原始URL"]


def collect_country(cc, name, keywords, max_pages):
    log.info("▶ %s(%s)", name, cc)
    bag, kw_map = {}, {}
    for kw in keywords:
        for page in range(1, max_pages + 1):
            jobs, has_more = fetch_search(cc, kw, page)
            if not jobs:
                break
            n0 = len(bag)
            for j in jobs:
                if j["id"] not in bag:
                    bag[j["id"]] = j
                    kw_map.setdefault(j["id"], []).append(kw)
            added = len(bag) - n0
            log.info("  [%s] %-26s p%d %d条(新增%d 累计%d)", cc, kw, page, len(jobs), added, len(bag))
            if not has_more:
                break
            if added == 0 and page > 1:
                break
            time.sleep(C.REQUEST_DELAY)
    for jid in bag:
        bag[jid]["_kw"] = ",".join(sorted(set(kw_map.get(jid, []))))
    log.info("✔ %s 去重后 %d 条", name, len(bag))
    return bag


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
    ap.add_argument("--kw", help="自定义关键词(逗号分隔)")
    ap.add_argument("--max-pages", type=int, default=C.MAX_PAGES_PER_KW)
    ap.add_argument("--no-detail", action="store_true")
    args = ap.parse_args()
    os.makedirs(DATA_DIR, exist_ok=True)
    countries = {args.country: C.COUNTRIES[args.country]} if args.country else C.COUNTRIES
    keywords = [k.strip() for k in args.kw.split(",")] if args.kw else C.KEYWORDS

    all_records = []
    for cc, name in countries.items():
        bag = collect_country(cc, name, keywords, args.max_pages)
        for jid, j in bag.items():
            detail = ("", "", "") if args.no_detail else fetch_detail(cc, j)
            if not args.no_detail:
                time.sleep(C.DETAIL_DELAY)
            r = build_record(cc, j, detail)
            r["匹配关键词"] = j.get("_kw", "")
            all_records.append(r)
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
