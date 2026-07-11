# Glints 电子信息工程岗位采集（纯协议）

采集 glints.com 的电子信息工程岗位，按 14 字段输出。
**覆盖**：SG 新加坡 / MY 马来西亚 / VN 越南（glints 市场不含菲律宾/泰国）。

## 一、机制（纯协议 GET + __NEXT_DATA__）

- **搜索**：`GET /{cc}/opportunities/jobs/explore?keyword={词}&country={CC}&page={n}`
  → HTML 含 `<script id="__NEXT_DATA__">` JSON → `pageProps.initialJobs.jobsInPage` = 岗位数组
- **详情**：`GET /{cc}/opportunities/jobs/{slug}/{id}` → `__NEXT_DATA__.pageProps.initialData.data`
  → 补岗位描述(Draft.js)/企业规模(company.size)/企业介绍(company.descriptionJsonString)
- **反爬**：Cloudflare → curl_cffi chrome 指纹 + 代理换 IP + 间隔 2s（参照 jobstreet 教训）

## 二、关键调研结论

1. **字段最全**（14 字段全有，含 hiredchina/jobstreet 没有的企业规模/介绍）
2. **不支持 category/行业过滤**（getJobSearchFilters 无此维度），只能 keyword 搜索
3. keyword 参数是 `keyword`（URL ?keyword=，非 ?q=）；graphql 字段被前端隐藏，故用 SSR __NEXT_DATA__
4. **glints 不覆盖菲律宾/泰国**（市场只有 SG/MY/VN/ID/CN/HK）

## 三、字段映射（14 字段，Y 全满足）

| 字段 | 来源 | Y |
|---|---|---|
| 招聘岗位名称 | title | Y |
| 招聘人数 | 默认 1 | Y |
| 经验要求 | minYearsOfExperience-maxYearsOfExperience | Y |
| 学历要求 | educationLevel（Diploma/Bachelor 等） | N |
| 企业名称 | company.name | Y |
| 工作地点 | city + location.formattedName | Y |
| 薪资待遇 | salaries（minAmount-maxAmount CurrencyCode） | Y |
| 公司行业 | company.industry.name | N |
| 企业规模 | company.size（11-50/51-200 等） | N |
| 企业介绍 | company.descriptionJsonString | N |
| 岗位描述 | descriptionJsonString（Draft.js 提纯文本） | Y |
| 招聘状态 | status（OPEN→Recruiting） | N |
| 原始URL | /{cc}/opportunities/jobs/{slug}/{id} | Y |

注：薪资 19999-20000 是 glints 占位值，已识别为"保密"。

## 四、运行

```bash
pip install -r requirements.txt   # curl_cffi
python main.py                    # SG/MY/VN × 21 电子关键词 × 3 页 + 详情
python main.py --country SG       # 单国
python main.py --kw "hardware engineer" --max-pages 5
```

输出 `data/jobs_latest.csv`（UTF-8-SIG）+ `.json`。

## 五、结果（5 国实际覆盖 3 国）

| 国家 | 岗位数 |
|---|---|
| SG 新加坡 | 187 |
| MY 马来西亚 | 39 |
| VN 越南 | 211 |
| PH/TH | glints 不覆盖 |
| **合计** | **437** |

Y 字段 100% 填充；薪资 31% 有数据（69% 雇主保密，标注"保密"）。
