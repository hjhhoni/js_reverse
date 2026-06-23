# import requests


# headers = {
#     "siteId": "35",
#     "Host": "app.xkb.com.cn",
#     "User-Agent": "okhttp/4.9.1"
# }
# url = "https://app.xkb.com.cn/xkbapp/fundapi/article/api/articles"
# params = {
#     "chnlId": "351",
#     "page": "1",
#     "size": "3",
#     "visibility": "2",
#     "keyword": ""
# }
# response = requests.get(url, headers=headers, params=params)

# print(response.text)
# print(response)

import requests

headers = {
    "Host": "frodo.douban.com",
    "user-agent": "Rexxar-Core/0.1.3 api-client/1 com.douban.frodo/7.18.0(230) Android/32 product/daoxiang vendor/OPPO model/PJJ110 brand/OPPO  rom/android  network/wifi  udid/5164583510308c4c1be9e382fba6052f0899f9f0  platform/mobile nd/1 com.douban.frodo/7.18.0(230) Rexxar/1.2.151  platform/mobile 1.2.151"
}
url = "https://frodo.douban.com/api/v2/subject_collection/movie_comedy"
params = {
    "updated_at": "",
    "for_mobile": "1",
    "udid": "5164583510308c4c1be9e382fba6052f0899f9f0",
    "rom": "android",
    "apikey": "0dad551ec0f84ed02907ff5c42e8ec70",
    "s": "rexxar_new",
    "channel": "Yingyongbao_Market",
    "timezone": "Asia/Shanghai",
    "device_id": "5164583510308c4c1be9e382fba6052f0899f9f0",
    "os_rom": "android",
    "apple": "c780cd3143c65f2048c05199aae27f64",
    "sugar": "460000",
    "loc_id": "108288",
    "_sig": "H6j7oEwr1wnnUwmhlsykQ7F7lW8=",
    "_ts": "1782185813"
}
response = requests.get(url, headers=headers, params=params)

print(response.text)
print(response)