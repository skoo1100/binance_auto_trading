import pandas as pd
from binance.enums import *
import apis.config as c

"""
symbol (str): 거래쌍, (예: "BTCUSDT", "ETHUSDT"). 거래하려는 암호화폐의 심볼
side (str): "BUY" 또는 "SELL" ("BUY": 매수, "SELL": 매도)
quantity (float): 주문 수량
price (float): 주문 가격 (지정가)
"""

# 시장가 주문 (현물 거래)
def order_market(symbol, side, quantity):
    order = c.client.order_market(
        symbol=symbol,
        side=side,
        quantity=quantity
    )
    return order

# 지정가 주문 (현물 거래)
def order_limit(symbol, side, quantity, price):
    if side == "BUY":
        order = c.client.order_limit_buy(
            symbol=symbol,
            quantity=quantity,
            price=str(price)
        )
    elif side == "SELL":
        order = c.client.order_limit_sell(
            symbol=symbol,
            quantity=quantity,
            price=str(price)
        )
    return order

# 현물 주문 취소
def close_orders(symbol):
    open_orders = c.client.get_open_orders(symbol=symbol)
    df = pd.DataFrame(open_orders)
    for index in df.index: 
        c.client.futures_cancel_order(symbol=symbol, orderId=df['orderId'][index])

def close_buy_orders(symbol):
    open_orders = c.client.get_open_orders(symbol=symbol)
    df = pd.DataFrame(open_orders)
    df = df[df['side'] == 'BUY']
    for index in df.index: 
        c.client.futures_cancel_order(symbol=symbol, orderId=df['orderId'][index])

def close_sell_orders(symbol):
    open_orders = c.client.get_open_orders(symbol=symbol)
    df = pd.DataFrame(open_orders)
    df = df[df['side'] == 'SELL']
    for index in df.index: 
        c.client.futures_cancel_order(symbol=symbol, orderId=df['orderId'][index])