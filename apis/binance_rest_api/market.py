import pandas as pd
from binance.client import Client
import apis.config as c

# 모든 코인 정보 불러오기
def get_all_market():
    client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)
    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']
    symbols_df = pd.DataFrame(symbols)
    
    return symbols_df

# 해당 코인 종목의 step_size(수량 단위), tick_size(가격 단위), min_notional(최소 주문 금액 {가격 * 수량})의 단위
def get_market_limits(symbol):
    client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)
    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']
    for sym in symbols:
        if sym['symbol'] == symbol:
            filters = sym['filters']
            limits = {}
            for f in filters:
                if f['filterType'] == 'PRICE_FILTER':
                    limits['tick_size'] = f['tickSize']
                elif f['filterType'] == 'LOT_SIZE':
                    limits['step_size'] = f['stepSize']
                elif f['filterType'] in ('MIN_NOTIONAL', 'NOTIONAL'):
                    limits['min_notional'] = f.get('minNotional')
            return limits
    return None