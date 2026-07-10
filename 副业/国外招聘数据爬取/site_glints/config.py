# -*- coding: utf-8 -*-
"""Glints 采集配置（纯协议 GET + __NEXT_DATA__ JSON 解析）
机制：GET /{cc}/opportunities/jobs/explore?keyword=&country=&page= -> HTML 含 __NEXT_DATA__ JSON
      -> pageProps.initialJobs.jobsInPage = 岗位数组（标准 JSON）
      详情 GET -> __NEXT_DATA__ 含岗位描述/企业规模/介绍
反爬：Cloudflare（curl_cffi chrome 指纹 + 代理换IP + 间隔）
覆盖：SG/MY/PH/VN/TH
"""
from urllib.parse import quote

BASE = "https://glints.com"
# 关键词搜索（keyword 文本匹配 title+description，country 国家过滤）
SEARCH_URL = BASE + "/{cc}/opportunities/jobs/explore?keyword={kw}&country={cc}&page={page}&pageSize=30"
DETAIL_URL = BASE + "/{cc}/opportunities/jobs/{slug}/{job_id}"

COUNTRIES = {
    "SG": "Singapore",
    "MY": "Malaysia",
    "PH": "Philippines",
    "VN": "Vietnam",
    "TH": "Thailand",
}

# 电子信息工程关键词（glints keyword 匹配 title+description，用专业词精准搜）
KEYWORDS = [
    "hardware engineer", "electronics engineer", "electrical engineer",
    "embedded engineer", "embedded software engineer", "firmware engineer",
    "fpga engineer", "rf engineer", "ic design engineer", "semiconductor engineer",
    "pcb engineer", "power electronics engineer", "field application engineer",
    "electronic engineer", "circuit design engineer", "verification engineer",
    "hardware", "embedded", "firmware", "fpga", "semiconductor", "electronics",
]

PAGE_SIZE = 30
REQUEST_DELAY = 2.0      # SERP 间隔（保守防 CF 限流）
DETAIL_DELAY = 1.2       # 详情间隔
MAX_RETRIES = 5
LIMIT_COOLDOWN = 45
MAX_PAGES_PER_KW = 5     # 每关键词最多取 5 页（电子岗精准，5页够）
PROXY = "http://127.0.0.1:10090"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
