# -*- coding: utf-8 -*-
"""验证 glints SSR HTML 是否含 RSC job 数据（方案可行性）"""
import sys, re, json
sys.stdout.reconfigure(encoding="utf-8")
from curl_cffi import requests

PROXY = "http://127.0.0.1:10090"
url = "https://glints.com/sg/opportunities/jobs/explore?keyword=hardware%20engineer&country=SG"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                               "Accept-Language": "en-US,en;q=0.9"},
                 proxies={"http": PROXY, "https": PROXY}, impersonate="chrome", timeout=30)
html = r.text
print("HTTP", r.status_code, "HTML size", len(html))

# 搜 RSC / job 数据标记
for kw in ["jobsInPage", "searchJobsV3", "minYearsOfExperience", "hasMore",
           "descriptionJsonString", "shouldShowSalary", "hierarchicalJobCategory",
           '"title"', "salaries"]:
    i = html.find(kw)
    print(f"  {kw:28} {'@'+str(i) if i>=0 else 'NO'}")

# 尝试找 RSC 里的 job JSON 块（Next.js RSC payload 常在 self.__next_f.push([...])）
pushes = re.findall(r"self\.__next_f\.push\(\[\d+,(\".*?\")\]\)", html, re.S)
print(f"\n__next_f.push 块数: {len(pushes)}")
# 看 job title 出现次数（判断 RSC 含岗位）
titles = re.findall(r'"title":"([^"]{5,60})"', html)
print(f'HTML 中 "title":"..." 出现 {len(titles)} 次，样例:')
for t in titles[:8]:
    print("   ", t)
