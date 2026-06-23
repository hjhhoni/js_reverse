import requests


headers = {
    "siteId": "35",
    "Host": "app.xkb.com.cn",
    "User-Agent": "okhttp/4.9.1"
}
url = "https://app.xkb.com.cn/xkbapp/fundapi/article/api/articles"
params = {
    "chnlId": "351",
    "page": "1",
    "size": "3",
    "visibility": "2",
    "keyword": ""
}
response = requests.get(url, headers=headers, params=params)

print(response.text)
print(response)