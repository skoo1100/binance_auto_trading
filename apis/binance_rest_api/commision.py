from binance.client import Client
import apis.config as c

# 선물 수수료 가져오기 (maker, taker)
def get_future_commission(symbol):
    client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)
    commission = client.futures_commission_rate(symbol=symbol)
    maker_commission = commission['makerCommissionRate']
    taker_commission = commission['takerCommissionRate']

    return {
        'maker_commission': maker_commission,
        'taker_commission': taker_commission
    }