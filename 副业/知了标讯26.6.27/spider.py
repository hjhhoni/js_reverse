import requests
import json
import time

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en,zh;q=0.9,zh-CN;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://www.zhiliaobiaoxun.com",
    "Pragma": "no-cache",
    "Referer": "https://www.zhiliaobiaoxun.com/search?key=12345",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Storage-Access": "active",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "auth-token": "eyJhbGciOiJIUzUxMiIsInppcCI6IkdaSVAifQ.H4sIAAAAAAAAAKtWykwsUbIyNLcwMjUxNDYy0VEqLk1SslIyMjA3NDZT0lFKrSgAylsYmhiYmwPlawHHOQwsMgAAAA.D9VKK0v03eWkUWHGi9UAtM4ZDP2xAlmEIEqOL547pFwpNYn9yAhfWuRUapPmBEd1K6Q-dHsKAeLtFWjSeogb4Q",
    "platform": "pc",
    "sec-ch-ua": "\"Google Chrome\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
url = "https://api-service-zhiliao.bailian-ai.com/search/bid"
params = {
    "userId": "207136",
    "page": "2",
    "count": "10",
    "bidProcesses": "70",
    "keyword": "12345",
    "timestamp": int(time.time() * 1000),
    "hash": "04270bdd910af6313e71e55667e215f7"
}
response = requests.get(url, headers=headers, params=params)

print(response.text)
print(response)