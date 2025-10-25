#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDOU 电费查询（requests 版）+ Bark 推送
- 自动登录 → 获取 token → 查宿舍电表 → 刷新抄表 → 查询最新数据
- 成功/失败均可通过 Bark 推送到手机

使用方法：
1) 安装依赖：pip install requests rich
2) 将 BARK_TOKEN 设置到环境变量或直接填到下方 DEFAULT_BARK_TOKEN
3) 运行：python electric_fee_query.py
"""
from __future__ import annotations
import os
import time
import random
import hashlib
import json
import urllib.parse
import requests
from typing import Any, Dict
from datetime import datetime

# ==== 可配置项 ====
STUDENT_NAME   = ""
STUDENT_OUTID  = ""   # 学工号/一卡通账号
STUDENT_PWD    = ""

# Bark：优先读环境变量 BARK_TOKEN（推荐），否则用此处默认值
DEFAULT_BARK_TOKEN = os.getenv("BARK_TOKEN", "")
BARK_ICON = "https://youke1.picui.cn/s1/2025/10/18/68f330c9a6487.jpg"

# 接口基地址
BASE = "https://cz.gdou.edu.cn/APIXCX"

# 关闭证书告警（校内自签场景常见）
requests.packages.urllib3.disable_warnings()  # type: ignore

# ==== 辅助 ====
HEADERS_JSON = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108 Safari/537.36",
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
}
HEADERS_FORM = {
    "User-Agent": HEADERS_JSON["User-Agent"],
    "content-type": "application/x-www-form-urlencoded",
}

def fmt_now() -> str:
    return datetime.now().strftime("[%Y-%m-%d][%H:%M:%S]")

# ==== Bark 推送 ====

def send_bark(topic: str, content: str, token: str | None = None) -> int | None:
    """发送 Bark 推送。
    :param topic: 标题
    :param content: 文本（会自动 URL 编码）
    :param token: 覆盖默认 token；为空则读取 DEFAULT_BARK_TOKEN；都为空则不推送
    :return: 状态码或 None
    """
    tk = (token or DEFAULT_BARK_TOKEN or "").strip()
    if not tk:
        return None
    # Bark 接口： https://api.day.app/<token>/<title>/<body>?icon=<url>
    # 题目/内容需 URL 编码，避免中文或换行造成 400
    title_q = urllib.parse.quote(topic)
    body_q  = urllib.parse.quote(content)
    url = f"https://api.day.app/{tk}/{title_q}/{body_q}?icon={urllib.parse.quote(BARK_ICON)}"
    try:
        r = requests.get(url, timeout=10)
        return r.status_code
    except Exception:
        return None

# ==== 登录与 token 获取 ====

def login_student() -> Dict[str, Any]:
    url = f"{BASE}/app/xcx/xkplogin"
    payload = {"outid": STUDENT_OUTID, "ecardPassword": STUDENT_PWD, "name": STUDENT_NAME}
    resp = requests.post(url, data=json.dumps(payload), headers=HEADERS_JSON, verify=False, timeout=20)
    return resp.json()

def get_app_token() -> str:
    # 按前端 JS： userName 固定 'szbdyb'，key 为 '4arcOUm6Wau+VuBX8g+IPg=='，签名算法 SHA-256
    user_name = "szbdyb"
    bdy_key   = "4arcOUm6Wau+VuBX8g+IPg=="
    now_ts = int(time.time())
    num = str(random.randint(999, 10000))
    sign_str = f"userName={user_name}&time={now_ts}&num={num}&key={bdy_key}"
    sign = hashlib.sha256(sign_str.encode()).hexdigest()
    url = f"{BASE}/app/xcx/login"
    resp = requests.post(url, headers=HEADERS_FORM, data={"userName": user_name, "time": now_ts, "num": num, "sign": sign}, verify=False, timeout=20)
    obj = resp.json()
    if obj.get("code") != 0:
        raise RuntimeError(f"login code != 0: {obj}")
    # 接口可能顶层返回 token，也可能在 data.token
    return obj.get("token") or (obj.get("data") or {}).get("token") or ""

# ==== 电表查询 ====

def get_meter_infoallmatch(token: str, phone: str) -> Dict[str, Any]:
    url = f"{BASE}/app/xcx/meterinfo/getMeterInfoallmatch"
    resp = requests.get(url, params={"token": token, "phone": phone, "type": 0}, headers=HEADERS_JSON, verify=False, timeout=20)
    data = resp.json()
    if data.get("code") != 0 or not data.get("data"):
        raise RuntimeError(f"getMeterInfoallmatch failed: {data}")
    return data["data"][0]

def refresh_meter(building_id: str, com_address: str) -> None:
    url = f"{BASE}/ypt/app/message/readMeter"
    params = {"buildingID": building_id, "comAddress": com_address, "dataItemID": "00057", "userName": "ass"}
    requests.get(url, params=params, headers=HEADERS_JSON, verify=False, timeout=20)

def get_meter_status(token: str, building_id: str) -> Dict[str, Any]:
    url = f"{BASE}/app/xcx/meterinfo/getMeterStatus1"
    resp = requests.get(url, params={"token": token, "buildingID": building_id}, headers=HEADERS_JSON, verify=False, timeout=20)
    data = resp.json()
    if data.get("code") != 0 or not data.get("data"):
        raise RuntimeError(f"getMeterStatus1 failed: {data}")
    return data["data"][0]

# ==== 主流程 ====

def main():
    # 1) 校验学生登录（用于早期失败提示）
    login_obj = login_student()
    print("登录成功，返回数据：\n", login_obj)

    # 2) 获取 app token
    token = get_app_token()
    print("获取到 token:", token)

    # 3) 通过学号查宿舍电表信息
    base_info = get_meter_infoallmatch(token, STUDENT_OUTID)
    print("查询到的宿舍电表信息:", base_info)

    building_id = base_info["roomID"]
    com_addr    = base_info["comaddress"]

    # 4) 先刷新抄表，再读状态
    print("正在刷新电表读数……")
    refresh_meter(building_id, com_addr)

    status = get_meter_status(token, building_id)

    # 5) 格式化输出
    print("电表信息如下：")
    for k in (
            "meterID","comAddress","onlineStatus","piplineName","type","meterData","leftMoney","preUseDay",
            "meterStatus","updateDateTime","price","remaining","yffye","bzdye","bzsye","submchID",
            "buildingID","buildingName","dayDCTimes","anotherName","piplineid","dskgdID","dskgdName"):
        if k in status:
            print(f"{k}: {status[k]}")

    # 6) Bark 推送（成功）
    now = fmt_now()
    topic = "电费查询成功"
    body_lines = [
        now,
        f"{status.get('piplineName', '')}",
        f"余额: {status.get('leftMoney', '')}",
        f"总电量(kWh): {status.get('meterData', '')}",
        f"更新时间: {status.get('updateDateTime', '')}",
    ]
    send_bark(topic, "\n".join(body_lines))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Bark 推送（失败）
        send_bark("电费查询失败", f"{fmt_now()}\n{e!r}")
        raise
