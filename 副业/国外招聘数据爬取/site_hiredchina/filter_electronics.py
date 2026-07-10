# -*- coding: utf-8 -*-
"""
电子信息工程岗位匹配器（强电子词匹配）

规则：岗位的「标题」或「描述」命中任一强电子关键词 -> 纳入。
强电子词 = 明确的电子信息工程术语（hardware/embedded/fpga/pcb/rf/ic/
semiconductor/firmware/power electronics/bms/antenna/vlsi/verilog…），
来自《电子信息工程岗位中英文对照.xlsx》223 岗位提炼。

为什么只匹配强词、且允许 title+description：
- hiredchina 标题普遍不规范（很多只写 Engineer/Manager），必须看描述补全
- 宽泛词（engineer/quality/test）跨行业，单独命中会误纳，故不采用
- 通配符 * 站点不支持、短词根(sem/comm/em)子串噪音大，故用完整词/长词根
"""
import re

# ============================================================
# 强电子关键词
# ============================================================
# token：整词匹配（\b 词边界），避免子串误判
STRONG_TOKENS = [
    # 芯片/IC/逻辑
    "fpga", "pcb", "mcu", "dsp", "asic", "vlsi",
    "verilog", "vhdl", "semiconductor", "microcontroller",
    # 硬件/固件/嵌入式
    "hardware", "firmware", "embedded", "emc",
    # 射频/天线/通信
    "antenna", "radar", "baseband", "rfid",
    # 光电/微机电
    "optoelectronic", "opto-electronic", "mems",
    # 物联网/无线
    "lora",
]

# phrase：短语子串匹配（已含上下文，精度高）
STRONG_PHRASES = [
    # 硬件
    "hardware engineer", "hardware development", "hardware design",
    "hardware lead", "hardware manager", "hardware architect",
    "board design", "board-level", "schematic", "pcb design", "pcb layout",
    # IC / 半导体
    "ic design", "ic engineer", "chip design", "chip engineer",
    "soc design", "soc engineer", "soc architect",
    "layout engineer", "verification engineer", "dft engineer",
    "mixed-signal", "mixed signal", "analog design", "analog engineer",
    "digital design",
    # 射频 / 天线 / 微波
    "rf engineer", "rf design", "radio frequency", "rfic",
    "antenna design", "microwave engineer", "rf power amplifier",
    "rf matching", "rf calibration", "rf simulation",
    # 嵌入式 / 固件
    "embedded engineer", "embedded software", "embedded system",
    "embedded linux", "embedded firmware", "embedded gui",
    "firmware engineer", "mcu firmware", "low power firmware",
    "rtos", "bsp engineer", "kernel driver", "device driver",
    # FPGA
    "fpga engineer", "fpga design", "fpga verification", "fpga timing",
    # 电源 / 电力电子
    "power electronics", "power electronic engineer", "switching power",
    "switch-mode", "switch mode power", "linear power",
    "battery management", "bms engineer", "inverter engineer",
    "servo drive", "pv converter", "charging pile", "power quality",
    "power supply engineer", "motor control",
    # 汽车/总线电子
    "can bus", "can/lin", "lin bus", "automotive ethernet",
    "adas", "automotive hardware", "automotive electronics",
    "automotive firmware", "automotive radar", "vehicle camera",
    # 物联网 / 传感
    "iot engineer", "iot development", "nb-iot", "nb iot",
    "sensor engineer", "mems sensor", "wearable hardware",
    # 光电 / 显示
    "optical engineer", "optoelectronic", "led driver", "display driver",
    "laser driver", "backlight", "optical module", "imaging system",
    # 测试 / EMC / 可靠性
    "emc engineer", "electromagnetic compatibility", "emi engineer", "emi rectification",
    "signal integrity", "power integrity", "si/pi",
    "failure analysis", "ate test",
    # FAE / 应用 / 现场
    "fae", "field application engineer",
    # 通用电子/电气
    "electronic engineer", "electronics engineer", "electrical engineer",
    "circuit design", "circuit engineer", "electrical design",
    "electronic design", "electronic hardware",
    # 电子方向算法/信号
    "signal processing", "dsp algorithm", "baseband algorithm",
    "radar signal", "image algorithm", "vision algorithm",
    # 通信设备
    "base station", "rf front-end", "rf front end",
    "telecom hardware",
    # 工艺 / SMT
    "smt process", "soldering", "pcba",
]

_TOKEN_RES = [(k, re.compile(r"\b" + re.escape(k) + r"\b", re.IGNORECASE)) for k in STRONG_TOKENS]


def match_strong(text):
    """返回命中的关键词（首个），未命中返回 None。"""
    if not text:
        return None
    low = text.lower()
    for k in STRONG_PHRASES:
        if k in low:
            return k
    for k, r in _TOKEN_RES:
        if r.search(text):
            return k
    return None


def is_electronic(job):
    """
    标题或描述命中任一强电子关键词 -> (True, '标题/描述:keyword')；否则 (False, '')。
    """
    title = job.get("title") or ""
    desc = job.get("description") or ""

    m = match_strong(title)
    if m:
        return True, f"标题:{m}"
    m = match_strong(desc)
    if m:
        return True, f"描述:{m}"
    return False, ""
