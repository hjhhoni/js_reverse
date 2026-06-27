from DrissionPage import Chromium, ChromiumPage
import os
import time
import random

all_page = 0
con = 0
start_time = time.time()
while True:
    all_page += 1
    browser = Chromium('127.0.0.1:9333')
    page = browser.latest_tab
    print(f"已连接到浏览器，当前页面标题: {page.title}")
    # lists = page.ele('.result-ul')
    lists = page.eles('.bidWrap')
    print(len(lists))
    for item in lists:
        row = {}
        row['标题'] = item.ele('tag:h3').text
        gs = item.ele('.companyinfo')
        gs = gs.eles('tag:p')
        row['招标公司'] = gs[1].text
        f = len(gs)
        row['中标公司'] = gs[3].text if f>=4 else '无'
        row['金额'] = item.ele('.brandInfo-money').text
        row['公告日期'] = item.ele('.brandInfo-date').text
        row['地区'] = item.ele('.brandInfo-area').text
        print(row)
        # 追加到csv文件
        con += 1
        with open(os.path.join(os.path.dirname(__file__), 'bid_info.csv'), 'a', encoding='utf-8') as f:
            f.write(f"{row['标题']},{row['招标公司']},{row['中标公司']},{row['金额']},{row['公告日期']},{row['地区']}\n")
    if all_page >= 300:
        break
    try:
        page.ele('.btn-next').click()
        time.sleep(random.randint(1, 3))
    except:
        break

print(f"爬取{all_page}页，共获取到{con}条数据，耗时{time.time()-start_time:.2f}秒")