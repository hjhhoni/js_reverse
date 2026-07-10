# -*- coding: utf-8 -*-
"""电子信息工程岗位过滤（glints）
按国家拉全量后本地过滤。glints SERP 仅有 title（无 description），故：
  A. title 命中强电子词 -> 纳入
  B. 行业/分类属电子 且 title 含工程词 -> 纳入
"""
import re

# 强电子 token（整词）
STRONG_TOKENS = [
    "fpga", "pcb", "mcu", "dsp", "asic", "vlsi",
    "verilog", "vhdl", "semiconductor", "microcontroller",
    "hardware", "firmware", "embedded", "emc",
    "antenna", "radar", "baseband", "rfid",
    "optoelectronic", "mems", "lora",
]
# 强电子短语
STRONG_PHRASES = [
    "hardware engineer", "hardware development", "hardware design",
    "ic design", "ic engineer", "chip engineer", "soc engineer",
    "rf engineer", "rf design", "radio frequency", "rfic",
    "antenna engineer", "microwave engineer",
    "embedded engineer", "embedded software", "embedded system", "embedded linux",
    "firmware engineer",
    "fpga engineer", "fpga design",
    "power electronics", "bms engineer", "inverter engineer",
    "electronic engineer", "electronics engineer", "electrical engineer",
    "circuit design", "circuit engineer", "electrical design",
    "signal processing", "baseband algorithm",
    "field application engineer", "fae",
    "pcba", "smt",
]
_TOKEN_RES = [re.compile(r"\b" + re.escape(k) + r"\b", re.I) for k in STRONG_TOKENS]

# 电子相关行业/分类关键词（glints industry.name / category.name 含这些算电子方向）
ELECTRONIC_INDUSTRIES = [
    "electronic", "semiconductor", "consumer electronic", "hardware",
    "electrical", "telecommunication", "automation", "robotic",
    "iot", "chip", "manufacturing",
]

_BROAD_ENG = re.compile(
    r"\b(engineer|engineering|technician|technical|developer|r&d)\b", re.I)


def has_strong(text):
    if not text:
        return None
    low = text.lower()
    for k in STRONG_PHRASES:
        if k in low:
            return k
    for k, r in zip(STRONG_TOKENS, _TOKEN_RES):
        if r.search(text):
            return k
    return None


def is_electronic(job):
    """返回 (bool, reason)。job 为 searchJobsV3 的 job 节点。"""
    title = job.get("title") or ""
    industry = ((job.get("company") or {}).get("industry") or {}).get("name") or ""
    cat = (job.get("hierarchicalJobCategory") or {}).get("name") or ""
    ind_cat = (industry + " " + cat).lower()
    is_elec_ind = any(k in ind_cat for k in ELECTRONIC_INDUSTRIES)

    m = has_strong(title)
    if m:
        return True, f"标题:{m}"
    if is_elec_ind and _BROAD_ENG.search(title):
        return True, f"行业:{industry[:20]}"
    return False, ""
