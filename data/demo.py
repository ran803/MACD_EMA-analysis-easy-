# 由于akshare和yfinance的数据获取不了，
# 所以从东方财富接口手动抓取 510300（沪深300ETF）的日线历史行情，
# 整理成 Backtrader 常用的 CSV 格式，并保存到当前脚本所在目录。
from pathlib import Path

import pandas as pd
# 和 requests 类似的 HTTP 请求库，但它更擅长模拟浏览器请求
from curl_cffi import requests


def download_hs300_etf():
    # 接口地址
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": "1.510300",
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": "101",
        "fqt": "0",
        "beg": "20200101",
        "end": "20250101",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "rtntype": "6",
    }

    response = requests.get(url, params=params, impersonate="chrome124", timeout=30)
    response.raise_for_status()
    payload = response.json()

    klines = payload.get("data", {}).get("klines", [])
    if not klines:
        raise ValueError("No kline data returned for 510300")

    rows = []
    for line in klines:
        parts = line.split(",")
        rows.append(
            {
                "Date": parts[0],
                "Open": float(parts[1]),
                "Close": float(parts[2]),
                "High": float(parts[3]),
                "Low": float(parts[4]),
                "Volume": int(float(parts[5])),
            }
        )

    df = pd.DataFrame(rows)
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

    out_path = Path(__file__).resolve().parent / "hs300etf.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"saved to: {out_path}")
    print(f"rows: {len(df)}")
    print(df.head())


if __name__ == "__main__":
    download_hs300_etf()
