# -*- coding: utf-8 -*-
"""
HiredChina.com 采集配置
- 目标接口：GET /api/v2/jobs?page=&limit=&where={"nationId":N}  （明文 JSON，无签名）
- 采集范围：5 国（新加坡 / 马来西亚 / 菲律宾 / 越南 / 泰国）
- 仅保留：电子信息工程相关岗位
"""
from urllib.parse import quote

# ============================================================
# 一、目标站点
# ============================================================
BASE_URL = "https://www.hiredchina.com"
LIST_API = BASE_URL + "/api/v2/jobs"
JOB_URL_TPL = BASE_URL + "/en/job/{line}"          # 原始 URL 模板（line = 岗位 UUID）

# 站点无登录态要求，仅需本地化 Cookie
COOKIES = {"NEXT_LOCALE": "en"}

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL + "/en/jobs",
    "Connection": "keep-alive",
}

PAGE_SIZE = 40          # 每页条数（站点实测 limit 无硬上限，40 稳妥）
REQUEST_DELAY = 1.0     # 每次请求间隔（秒），对 Cloudflare 友好
MAX_RETRIES = 6         # 单请求最大重试（Cloudflare 偶发 TLS 重置需多次）
RETRY_BACKOFF_BASE = 2  # 退避基数（指数：2,4,8,16,20,20 秒）

# ============================================================
# 二、目标国家（id 由站点 /api/v2/jobs 的 nationId 字段聚合得到）
# ============================================================
COUNTRIES = {
    152: "Singapore",
    102: "Malaysia",
    133: "Philippines",
    186: "Vietnam",
    171: "Thailand",
}

# ============================================================
# 三、i18n 翻译表（support.* key -> 可读值）
#    数据由站点实际返回的 key 聚合，精确覆盖 5 国数据
# ============================================================

# 薪资（规则：必须为数据 -> 输出数值范围；货币为 RMB/月）
# keep.secret = 站点对薪资保密，无任何数值 -> 标注「保密」
SALARY_MAP = {
    "support.salarie.under.10k": "<10000",
    "support.salarie.10k.-.15k": "10000-15000",
    "support.salarie.15k.-.20k": "15000-20000",
    "support.salarie.20k.-.25k": "20000-25000",
    "support.salarie.25k.-.30k": "25000-30000",
    "support.salarie.more.than.30k": "≥30000",
    "support.salarie.30k.-.35k.rmb.per.month": "30000-35000",
    "support.salarie.35k.-.40k.rmb.per.month": "35000-40000",
    "support.salarie.40k.-.45k.rmb.per.month": "40000-45000",
    "support.salarie.45k.-.50k.rmb.per.month": "45000-50000",
    "support.salarie.50k.-.60k.rmb.per.month": "50000-60000",
    "support.salarie.60k.-.70k.rmb.per.month": "60000-70000",
    "support.salarie.70k.-.80k.rmb.per.month": "70000-80000",
    "support.salarie.80k.-.90k.rmb.per.month": "80000-90000",
    "support.salarie.90k.-.100k.rmb.per.month": "90000-100000",
    "support.salarie.keep.secret": "保密",      # 站点保密，无数值
}

# 经验要求（规则：有哪种就提供哪种）
EXP_MAP = {
    "support.workingyears.less.than.one.year": "Less than 1 year",
    "support.workingyears.1～3.years": "1-3 years",
    "support.workingyears.3～5.years": "3-5 years",
    "support.workingyears.5～10.years": "5-10 years",
    "support.workingyears.more.than.10.years": "More than 10 years",
    "support.workingyears.unlimited.experience": "Unlimited",
}

# 雇佣类型
EMPLOYMENT_MAP = {
    "support.employment.full-time": "Full-time",
    "support.employment.part-time": "Part-time",
}

# 行业
INDUSTRY_MAP = {
    "support.industrie.agriculture.&.forestry.&.fishing": "Agriculture & Forestry & Fishing",
    "support.industrie.artificial.intelligence.&.iot.&.robot": "AI & IoT & Robot",
    "support.industrie.banking.&.finance": "Banking & Finance",
    "support.industrie.clothing.&.textile": "Clothing & Textile",
    "support.industrie.communication.network.equipment": "Communication & Network Equipment",
    "support.industrie.computer.software": "Computer Software",
    "support.industrie.consulting": "Consulting",
    "support.industrie.consumer.electronic.&.hi-tech": "Consumer Electronic & Hi-Tech",
    "support.industrie.culture.media": "Culture & Media",
    "support.industrie.data.service": "Data Service",
    "support.industrie.e-commerce": "E-Commerce",
    "support.industrie.education.&.training": "Education & Training",
    "support.industrie.engineering.&.manufacturing": "Engineering & Manufacturing",
    "support.industrie.engineering.construction": "Engineering & Construction",
    "support.industrie.game": "Game",
    "support.industrie.healthcare": "Healthcare",
    "support.industrie.hospitality": "Hospitality",
    "support.industrie.human.resources": "Human Resources",
    "support.industrie.it": "IT",
    "support.industrie.logistics": "Logistics",
    "support.industrie.marketing": "Marketing",
    "support.industrie.others": "Others",
    "support.industrie.real.estate": "Real Estate",
    "support.industrie.retail": "Retail",
    "support.industrie.trading": "Trading",
    "support.industrie.travel": "Travel",
}

# 招聘状态（站点全部为 approved；结合 isOnline 进一步标注）
STATE_MAP = {
    "support.statetype.approved": "Recruiting",      # 在招
}

# 国家 key -> 名
NATION_MAP = {
    "support.nationalitie.singapore": "Singapore",
    "support.nationalitie.malaysia": "Malaysia",
    "support.nationalitie.philippines": "Philippines",
    "support.nationalitie.vietnam": "Vietnam",
    "support.nationalitie.thailand": "Thailand",
}

AREA_MAP = {
    "support.area.others": "",
    "support.area.overseas": "",
}


def build_where(where_dict):
    """构造 where 查询参数（JSON -> url encode）。"""
    return quote(json_dumps(where_dict))


def json_dumps(obj):
    import json
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
