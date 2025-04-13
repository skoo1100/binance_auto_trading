import talib
import numpy as np

def rsi_strategy(data, used = True, period=14, threshold=50):
    """
    RSI 계산
    :param data: 종목 데이터 (가격 리스트)
    :param period: RSI 계산 기간 (기본 14일)
    :param threshold: 기준 RSI 값 (기본 50)
    :return: RSI 신호 (BUY / SELL / HOLD)
    """
    if not used:
        return None
    close_prices = np.array([item["close"] for item in data], dtype=np.float64)
    rsi_values = talib.RSI(close_prices, timeperiod=period)
    prev_rsi = rsi_values[-2]
    curr_rsi = rsi_values[-1]
    if prev_rsi < threshold and curr_rsi > threshold:
        return 'BUY'
    elif prev_rsi > threshold and curr_rsi < threshold:
        return 'SELL'
    else:
        return 'HOLD'

def macd_strategy(data, fastperiod=12, slowperiod=26, signalperiod=9):
    """
    MACD 신호 계산
    :param data: 종목 데이터 (가격 리스트)
    :param fastperiod: 빠른 이동 평균 기간 (기본 12일)
    :param slowperiod: 느린 이동 평균 기간 (기본 26일)
    :param signalperiod: 신호선 기간 (기본 9일)
    :return: MACD 신호 (BUY / SELL)
    """
    close_prices = np.array([item["close"] for item in data], dtype=np.float64)  # 종가 데이터 가져오기
    macd, macdsignal, macdhist = talib.MACD(close_prices, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    # MACD 신호 (MACD 라인과 Signal 라인 비교)
    if macd[-1] > macdsignal[-1]:
        return "BUY"
    else:
        return "SELL"

def triple_rsi_strategy(data, rsi_short_period=5, rsi_mid_period=30, rsi_long_period=60, threshold=20, ema_period=400):
    """
    Triple RSI 전략 + EMA 200 필터
    :param data: 종목 데이터 (가격 리스트)
    :param rsi_short_period: 단기 RSI 기간 (기본 7일)
    :param rsi_mid_period: 중기 RSI 기간 (기본 14일)
    :param rsi_long_period: 장기 RSI 기간 (기본 21일)
    :param threshold: 기준 RSI 값 (기본 50)
    :param ema_period: EMA 기간 (기본 200일)
    :return: RSI 신호 (BUY / SELL / HOLD)
    """
    close_prices = np.array([item["close"] for item in data], dtype=np.float64)
    rsi_short = talib.RSI(close_prices, timeperiod=rsi_short_period)
    rsi_mid = talib.RSI(close_prices, timeperiod=rsi_mid_period)
    rsi_long = talib.RSI(close_prices, timeperiod=rsi_long_period)
    ema200 = talib.EMA(close_prices, timeperiod=ema_period)
    
    prev_rsi_short, curr_rsi_short = rsi_short[-2], rsi_short[-1]
    prev_rsi_mid, curr_rsi_mid = rsi_mid[-2], rsi_mid[-1]
    prev_rsi_long, curr_rsi_long = rsi_long[-2], rsi_long[-1]
    curr_ema200 = ema200[-1]
    
    if curr_rsi_short > threshold and curr_rsi_short > curr_rsi_mid > curr_rsi_long:
        if close_prices[-1] > curr_ema200:
            return 'BUY'
    elif curr_rsi_short < threshold and curr_rsi_short < curr_rsi_mid < curr_rsi_long:
        if close_prices[-1] < curr_ema200:
            return 'SELL'
    return 'HOLD'