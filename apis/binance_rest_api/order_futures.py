import pandas as pd
from binance.client import Client
from binance.enums import *
from utils.round import round_value
import apis.config as c

# 시장가 주문 (선물 거래)
def order_futures_market(symbol, side, quantity):
    client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)
    if side == 'BUY' or side == 'SELL':
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
        return order
    else:
        return None

# 지정가 주문 (선물 거래)
def order_futures_limit(symbol, side, quantity, price, reduce_only = False):
    client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)
    if side == 'BUY' or side == 'SELL':
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_LIMIT,
            quantity=str(quantity),
            price=str(price),
            timeInForce=TIME_IN_FORCE_GTC,
            reduceOnly=reduce_only
        )
        return order
    else:
        return None

# 손절 주문 (선물 거래)
def order_futures_stop_market(symbol, side, quantity, stop_price, reduce_only = False):
    client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)
    if side == 'BUY' or side == 'SELL':
        client.futures_create_order(
            symbol=symbol,
            side=side,
            type=FUTURE_ORDER_TYPE_STOP_MARKET,
            stopPrice=str(stop_price),
            closePosition=False,
            quantity=str(quantity),
            timeInForce=TIME_IN_FORCE_GTC,
            reduceOnly=reduce_only,
            workingType='MARK_PRICE'
        )

# 선물 주문 취소
def close_futures_orders(symbol, side = None):
    client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)
    open_orders = client.futures_get_open_orders(symbol=symbol)
    if not open_orders:
        return
    df = pd.DataFrame(open_orders)
    if side == 'BUY' or side == 'SELL':
        df = df[df['side'] == side]
    for index in df.index: 
        client.futures_cancel_order(symbol=symbol, orderId=df['orderId'][index])

# 현재 보유 중인 선물 포지션(Long, Short, Flat) 판단
def get_direction(symbol):
    client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)
    position_information = client.futures_position_information(symbol=symbol)
    if not position_information:
        return 'FLAT'
    df = pd.DataFrame(position_information)
    if 'positionAmt' not in df.columns:
        return 'FLAT'
    df['positionAmt'] = df['positionAmt'].astype(float)
    if df['positionAmt'].sum() > 0:
        return 'LONG'
    elif df['positionAmt'].sum() < 0:
        return 'SHORT'
    else:
        return 'FLAT'

# take profit, stop loss 계산
def calculate_tp_sl(symbol, tp, sl, direction, tick_size):
    try:
        client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)
        position_information = client.futures_position_information(symbol=symbol)
        df = pd.DataFrame(position_information)
        df = df.loc[df['positionAmt'] != '0.000']
        entry_price = float(df.iloc[0]['entryPrice'])
        position_amt = abs(float(df.iloc[0]['positionAmt']))
        if direction == "LONG":
            tp_price = round_value(entry_price * (1 + tp / 100), tick_size)
            sl_price = round_value(entry_price * (1 - sl / 100), tick_size)
        elif direction == "SHORT":
            tp_price = round_value(entry_price * (1 - tp / 100), tick_size)
            sl_price = round_value(entry_price * (1 + sl / 100), tick_size)
        else:
            return entry_price, None, None, None
        return entry_price, tp_price, sl_price, position_amt
    except:
        return None, None, None, None

# 포지션에 따른 tp 주문
def place_tp_order(symbol, price, position_amt, direction):
    try:
        if direction == 'LONG':
            order_futures_limit(symbol, 'SELL', position_amt, price, True)
        elif direction == 'SHORT':
            order_futures_limit(symbol, 'BUY', position_amt, price, True)
        return
    except:
        return None

# 포지션에 따른 sl 주문
def place_sl_order(symbol, price, position_amt, direction):
    try:
        if direction == 'LONG':
            order_futures_stop_market(symbol, 'SELL', position_amt, price, True)
        elif direction == 'SHORT':
            order_futures_stop_market(symbol, 'BUY', position_amt, price, True)
        return
    except:
        return None