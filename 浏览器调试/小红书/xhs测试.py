# -*- coding:utf-8 -*- 
# Author: luoge
import subprocess
from functools import partial

# 强制 subprocess.Popen 使用 UTF-8 编码
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import requests
import hashlib
import json
import execjs
import time

try:
    from loguru import logger
except Exception as e:
    print("loguru 导入失败，改用 print:", e)
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

_ts = str(round(time.time() * 1000))

with open("xhs测试1.js", encoding="utf-8") as f1:
    cde = f1.read()

ctll = execjs.compile(cde)


def to_xhs_path(endpoint: str, data: dict) -> str:
    """
    把接口路径 + 数据字典 转换成小红书风格的字符串
    示例：/api/sns/web/v1/homefeed{...紧凑json...}
    """
    # separators=(',', ':') 去掉所有空格
    # ensure_ascii=False 防止中文被转义（如果有的话）
    json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)

    # boolean 转成小写（json.dumps 默认是小写，但保险起见）
    json_str = json_str.replace('True', 'true').replace('False', 'false')

    return f"{endpoint}{json_str}"


def md5(aaa):
    md5 = hashlib.md5()
    md5.update(aaa.encode())
    return md5.hexdigest()


def aa():
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://www.xiaohongshu.com",
        "priority": "u=1, i",
        "referer": "https://www.xiaohongshu.com/",
        "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "x-b3-traceid": "673d684cf53e35cb",
        "x-rap-param": "ByQBBAAAAAEAAAAUAAABFNUv2KUAACcRAAAAJAAAAAAAAAAAa2JwZ4SIXKMTsNzGll1k3a7yL80AAAAQdVR1Ea8hC7drs5+gJAvuj+HOuPO4moRSJRl4fDdpwuPqxQpCUO/55X7aW9CaJbjDZKDC6ykJ6XgGCm9jJWD2FZQFuOQ/GnHnluhswjskhDLa2APU9e/kEZ13uKh8sYXTlKcXVveHc+aUG1bToEchpvbepsK5Dt4osspogy+X+0gU1NXE3JmlN0yPTznEGAjMSeyUgKL3/r44JZerThmFLIJWo4msJxKAWdZr/pft21hMiDyGnIfN/kebpCsr9e+xedQgV/JRnSffxwnFTmugKhX1pNCgke9IRI6TOzNfb562H/4oXivWXswKt7bJv4AonTadtqgIO3+ezCNTpm/KytNjO6zBdtoN+pG5EgWlBI8AAAEE",
        "x-s": "XYS_2UQhPsHCH0c1PUhFHjIj2erjwjQhyoPTqBPT49pjHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQTJdPIPAZlg94aGLTlLLMAcgbAnoSp+dpbqemk8emxLepO8f+awepnJLTx2bSoyFDUyfEd+7iF8oSk4b8zpdzdqBD6LgSI+bpF4/QVJLRpzepj8fS/y9RDpozCJpb64pcM2rEotMLh4SzaPf4pzBEgJ7bpzLlnPnzpc/4mPrkHaMY/aSYPzaVlPB8+c9EIqMQCLDkcpnbLP9II2rT/Jfznnfl0yLLIaSQQyAmOarEaLSz+G0qAzebYyDRoq740p7+n4n4/nbplcUHVHdWFH0ijJ9Qx8n+FHdF=",
        "x-s-common": "2UQAPsHC+aIjqArjwjHjNsQhPsHCH0rjNsQhPaHCH0c1PUhFHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQhyoPTqBPT49pjHjIj2ecjwjH9N0L1PaHVHdWMH0ijP/SY+nLMP/L9weq78AYS8gqIy/mIJAGIyoSAy08jGd4l8B8I+ezIGgPMPeZIPerlPeGA+jHVHdW9H0ijHjIj2eqjwjHjNsQhwsHCHDDAwoQH8B4AyfRI8FS98g+Dpd4daLP3JFSb/BMsn0pSPM87nrldzSzQ2bPAGdb7zgQB8nph8emSy9E0cgk+zSS1qgzianYt8p+1/LzN4gzaa/+NqMS6qS4HLozoqfQnPbZEp98QyaRSp9P98pSl4oSzcgmca/P78nTTL08z/sVManD9q9z1J9p/8db8aob7JeQl4epsPrz6agW3Lr4ryaRApdz3agYDq7YM47HFqgzkanYMGLSbP9LA/bGIa/+nprSe+9LI4gzVPDbrJg+P4fprLFTALMm7+LSb4d+kpdzt/7b7wrQM498cqBzSpr8g/FSh+bzQygL9nSm7qSmM4epQ4flY/BQdqA+l4oYQ2BpAPp87arS34nMQyFSE8nkdqMD6pMzd8/4SL7bF8aRr+7+rG7mkqBpD8pSUzozQcA8Szb87PDSb/d+/qgzVJfl/4LExpdzQ4fRSy7bFP9+y+7+nJAzdaLp/2LSiz/Qz+FSpagYTLrRCJnRQyn+G8pm7zDS9yLPUcfpAzoi7q7Yn4BzQ408S8eq78pSx4p8QzLbAypSC8d4n4FSQye8SynrIqA8U87+Lqg4Oqf49qM4M4r+Q2BSU/Bbd8/ml4rbPwnRApM87/FShJB4QP7mhJM878gkl4AzsGp40aSP6qAmm/7P94gzdaLL98Lzp+d+hqob9agGM8nTx+npf2SQEaL+NqAmM49MQ4flE4Mm7/rEn4e8QPFRSygpF8rSk+7+npdz8a/+D8pzn4FldLozLz7pF2DS3qozQyBQb4e4QLDkP4fLAqgcEaLprGLS3Po+g4gzUNM+Pt9P6ad+rcSShanSQ/eQM4rTU4g4/aL+Dq9Tc4rzOLFTSPn+m8/b8nDTQyLTS2Bc98/mn4MH6pdzFa/P7q9kc4e8Qy/4APppM2LSea7+D8DRSzbmFLFSh87+h4g4MPf8gcDSb/eQQc94ApDF98p8fPBpDGf4Anpm7/DS3ypYQ2BV7qS8FJFS9y9kQyApAy7mlPFW6N7+xpd4ca/+gnrTl4986qe4SpUuIqAbc4bpYpdzEa/+k/FSiy9zH4gzaLgp7+LDA+d+hy04AypmFz7Sc4BQQy/YU8p8FpLDAygkSapiFanTmqM8scg+/8FkSPMm7zSbl4B4QypZ6agYNqA8l4bpQcA4SyFlLyDSe/nS6nnTwanYIqFS9+9pxLo4P/bmFp9Rn4r8QP7H9ag86q7W6PBp3qg4QGF8nJDSi/oQILoclqdbF/DDAaBbQPAYlanDFpDSiN9phJFbA+dmL+dzM494Qc9+QGM87wrEc4AQQyrTSzBQHzrS3aBQdJFkSzbmFpfQn4b8UG9P6cfRkPFShG0bI4g4OanDIq7YSngYQy9Qr4b87LDSkyM4zLoc7JMmF2DSb4/+QyecEag8z87+c47pQynYxanYwqA8n4MzjGAYSag8Q/FSb+g+LJ0+APpm7tFS9L/+QyBSxGppH2rS9JBYongHEag89q98/PBL9LoqEanYOq98c4b+QyrSHaLLIq9zM47bQ4flccSm7/LSead+DnfYON7pF8LYc4oQQ4fzS8obFJFS9/dPlL7i6aLP7q9zI/7+8pdzULLb6qMSn4AQAJFEAygpF2DSh/7+kn/pSpMmFqrSiae8QyUTTLgb7n/QVq0FjNsQhwaHCN/PA+AqU+eDA+sIj2erIH0iINsQhP/rjwjQ1J7QTGnIjNsQhP/HjwjHl+AqMw/DUPAZFw/qFwAr7+ALl+AL7wecEPePjKc==",
        "x-t": "1775992308929",
        "x-xray-traceid": "cec0b202571419f8893d68e22d05659c",
        "xy-direction": "6"
    }
    cookies = {
        "abRequestId": "435da070-a8ca-5eb6-9456-004b44d3f6ac",
        "a1": "19dd31753ee6i6ml8c015a90588j5fs7sex4auex350000277585",
        "gid": "yjffqyWWSfMJyjffqyW2qd7dddK3K61YS8y2CCq0j82YY428V2iMW0888JWW2Y28DyKYKKJ8",
        "web_session": "030037aec33c3963bd75012e882e4aefd1fa68",
    }
    url = "https://edith.xiaohongshu.com/api/sns/web/v1/homefeed"
    data = {
        "cursor_score": "",
        "num": 18,
        "refresh_type": 1,
        "note_index": 10,
        "unread_begin_note_id": "",
        "unread_end_note_id": "",
        "unread_note_count": 0,
        "category": "homefeed.cosmetics_v3",
        "search_key": "",
        "need_num": 8,
        "image_formats": [
            "jpg",
            "webp",
            "avif"
        ],
        "need_filter_image": False
    }
    result = to_xhs_path("/api/sns/web/v1/homefeed", data)
    print("转数据格式-->" + result)
    bb = md5(result)
    print("加密arg1-->" + bb)
    cc = md5("/api/sns/web/v1/homefeed")
    print("加密arg2-->" + cc)
    sign = ctll.call("get_sign", result, bb, cc)
    print("加密x-s-->" + sign)
    headers['x-s'] = sign
    headers['x-t'] = _ts
    data = json.dumps(data, separators=(',', ':'))
    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    print("输出->" + response.text)
    """
    "/api/sns/web/v1/homefeed{"cursor_score":"","num":18,"refresh_type":1,"note_index":10,"unread_begin_note_id":"","unread_end_note_id":"","unread_note_count":0,"category":"homefeed.cosmetics_v3","search_key":"","need_num":8,"image_formats":["jpg","webp","avif"],"need_filter_image":false}"
    
    "d3799817a666146f76984d1734bb4eb4"
    
    "6cb167ba87e1a756420d916fc234803c"
    """


aa()
