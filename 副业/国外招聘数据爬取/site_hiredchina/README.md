# HiredChina 电子信息工程岗位采集（纯协议）

采集 `https://www.hiredchina.com/en/jobs` 上 **新加坡 / 马来西亚 / 菲律宾 / 越南 / 泰国** 五国的
**电子信息工程相关岗位**，按《爬虫说明.md》14 字段输出 CSV / JSON。

## 一、接口分析

| 项 | 值 |
|---|---|
| 列表接口 | `GET https://www.hiredchina.com/api/v2/jobs?page={p}&limit={n}&where={"nationId":{id}}` |
| Method | GET |
| 鉴权 | 无登录态；仅需 Cookie `NEXT_LOCALE=en` |
| 签名/加密 | **无**（明文 JSON，无 sign / token / 加密参数） |
| 反爬 | Cloudflare 边缘；普通浏览器 UA + 请求间隔即可稳定通过 |
| 响应 | `{"code":0,"data":{"count":N,"list":[...]}}` 明文 JSON |

**结论：纯协议（requests）即可，无需浏览器、无需逆向签名。** 已用 `curl` 与 `requests` 双向验证。

### 过滤能力（实测）
- `where.nationId` —— 按国家过滤 ✅（有效）
- `where.kw` —— 关键词搜索（标题+描述）✅（有效）
- `where.areaKey` / `where.post` —— 站点忽略 ❌

为保证「电子信息工程岗位」的**召回完整性**，采用「逐国拉全量 + 本地关键词过滤」，
而非依赖站点关键词搜索（站点 kw 召回不全）。

## 二、国家 ID（由 nationId 字段聚合得到）

| 国家 | nationId |
|---|---|
| Singapore 新加坡 | 152 |
| Malaysia 马来西亚 | 102 |
| Philippines 菲律宾 | 133 |
| Vietnam 越南 | 186 |
| Thailand 泰国 | 171 |

## 三、电子信息工程过滤规则（`filter_electronics.py`，强电子词匹配）

关键词来源：`电子信息工程岗位中英文对照.xlsx`（223 岗位 / 17 大类）。

**规则**：岗位的「标题」或「描述」命中任一**强电子关键词**即纳入（标题命中排前）。
强电子词 = 明确的电子信息工程术语，整词/长短语匹配：

- **芯片/IC**：fpga / pcb / mcu / dsp / asic / soc / vlsi / verilog / vhdl / semiconductor / microcontroller / ic design / layout engineer / verification engineer
- **硬件/嵌入式/固件**：hardware / embedded / firmware / rtos / bsp / schematic / board design
- **射频/天线/通信**：rf engineer / antenna / radar / baseband / rfic / microwave
- **电源/电力电子**：power electronics / bms / inverter / servo / charging pile / motor control
- **光电/显示**：optical / optoelectronic / led driver / display driver
- **测试/EMC/工艺**：emc / signal integrity / failure analysis / ate test / smt process / pcba
- **通用电子/电气**：electronic(s) engineer / electrical engineer / circuit design
- **现场应用**：fae / field application engineer

> 为什么这样设计（实测 hiredchina 得出）：
> - 站点搜索框**不支持通配符 `*`**（`electr*` 返回全站），kw 是 title+description 子串匹配
> - 短词根（`sem`/`comm`/`em`）子串噪音爆炸（"communication skills" 误纳造价师/教练）
> - 故用**完整词/长词根 + 词边界**匹配，title+description 双覆盖（标题普遍不规范，须看描述）
> - 宽泛词（engineer/quality/test）跨行业不纳入，避免误判

CSV 末尾附「匹配关键词」列（标注 `标题:xxx`/`描述:xxx`，标题命中排前）；JSON 额外含 `_匹配原因`。

## 四、字段映射（14 字段）

| # | 字段 | 数据来源 | 处理 |
|---|---|---|---|
| 1 | 招聘岗位名称 | `title` | 原样 |
| 2 | 招聘人数 | —— | 站点无此字段，按规则**默认 1** |
| 3 | 经验要求 | `workingYearsKey` | 翻译（1-3 years 等） |
| 4 | 学历要求 | 描述识别 | 站点 `qualificationKey` 全站为空，从描述识别 Bachelor/Master/PhD（面向本科及以上），多数为空 |
| 5 | 企业名称 | `companyName` | 原样 |
| 6 | 企业类型 | —— | 站点无结构化数据，留空 |
| 7 | 工作地点 | `overseasArea`+`nationKey` | 优先 `overseasArea`（站点真实城市/地址，约 36% 有值，如 "Malaysia · 怡保"）；空则国家名。`areas` 字段对 5 国仅 overseas/others，不采用 |
| 8 | 薪资待遇(RMB/月) | `salaryKey` | 数值范围；`keep.secret`→`保密`（站点保密，描述也无薪资） |
| 9 | 公司行业 | `company.industryKey` | 翻译 |
| 10 | 企业规模 | —— | 站点无结构化数据，留空 |
| 11 | 企业介绍 | —— | 站点公司页仅含 {名称,行业,网站,logo}，无介绍，留空 |
| 12 | 岗位描述 | `description` | 原样保留英文 |
| 13 | 招聘状态 | `stateTypeKey` | approved→Recruiting(在招) |
| 14 | 原始URL | `line` | `https://www.hiredchina.com/en/job/{line}` |

> 字段 6/10/11 留空符合规则「按原网站，没有就没有」。

## 五、运行

```bash
pip install -r requirements.txt

python main.py                # 全量采集 5 国 -> 硬核电子岗（jobs_latest）
python main.py --country 152  # 仅新加坡
python main.py --test         # 每国仅首页（快速验证）
python main.py --no-filter    # 不过滤，导出全量 1050 条（调试）
```

输出（`data/`）：`jobs_electronic_{时间戳}.csv|.json` + `jobs_latest.csv|.json`（= 硬核电子岗，默认交付件）。
CSV 为 UTF-8-SIG（Excel 直开），末尾「匹配关键词」列标注命中来源；JSON 额外含 `_匹配原因`。

## 六、最近一次结果（5 国全量 1050 条，经 API count 完整性校验零缺失）

| 国家 | 岗位总数 |
|---|---|
| Singapore | 172 |
| Malaysia | 272 |
| Philippines | 84 |
| Vietnam | 257 |
| Thailand | 265 |
| **合计** | **1050** |

**强电子词匹配命中：41 条**（标题命中 11 + 描述命中 30）—— hiredchina 5 国硬核电子岗上限。

## 七、已知限制

1. **薪资保密**：约 44% 岗位站点设为 `keep.secret`，描述亦无薪资 → 标注 `保密`（非采集缺陷）。
2. **学历**：站点 `qualificationKey` 全站为空，仅能从描述轻量识别，覆盖率低。
3. **公司规模/类型/介绍**：站点公司页无结构化字段，无法采集（按规则留空）。
4. **工作地点城市**：5 国岗位的城市在 `overseasArea` 字段（约 36% 有值，如吉隆坡/曼谷/胡志明/怡保/Manila），约 64% 雇主未填具体城市，仅能给出国家名。`areas` 字段对 5 国基本无效。
5. 本站以中国外教为主，东南亚电子岗位存量有限（36 条为全站全量）。

## 八、调度（每周更新）

交付频率为每周一次，可配合定时任务：
```bash
# Linux crontab：每周一 09:00
0 9 * * 1 cd /path/to/site_hiredchina && python main.py >> data/run.log 2>&1
```
