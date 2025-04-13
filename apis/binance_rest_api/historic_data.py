import pandas as pd
import pytz
from datetime import datetime, timedelta
from binance.client import Client
import apis.config as c

# 과거 데이터 가져오기
def get_historic_data(symbol, interval, start_date = (datetime.now(pytz.utc) - timedelta(days=1)).strftime("%Y-%m-%d"), end_date = (datetime.now(pytz.utc) + timedelta(days=1)).strftime("%Y-%m-%d")):
    """
    symbol (str): 거래쌍 (예: "BTCUSDT", "ETHUSDT"). 거래하려는 암호화폐의 심볼
    interval (str): 캔들 간격 (예: "1m", "5m", "15m", "1h", "1d" 등)
    start_date (str): 시작 날짜 (형식: "YYYY-MM-DD")
    end_date (str): 종료 날짜 (형식: "YYYY-MM-DD") (default: 오늘 날짜)
    """
    client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)

    start_ts = int(pd.Timestamp(start_date).timestamp() * 1000)
    end_ts = int(pd.Timestamp(end_date).timestamp() * 1000)

    limit = 1000
    all_data = []
    cur_ts = start_ts

    while cur_ts < end_ts:
        klines = client.get_klines(symbol=symbol, interval=interval, startTime=cur_ts, endTime=end_ts, limit=limit)
        if not klines:
            break
        # [시작시간, 시가, 고가, 저가, 종가, 거래량]
        for k in klines:
            all_data.append({
                "timestamp": k[0],
                "time": pd.to_datetime(k[0], unit="ms"),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5])
            })
        last_time = klines[-1][0]
        if len(klines) < limit:
            break
        cur_ts = last_time + 1

    return all_data