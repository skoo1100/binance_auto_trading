from binance.client import Client
import apis.config as c

# 코인 종목의 레버리지 불러오기
def get_leverage(symbol):
    """
    symbol (str): 거래쌍, (예: "BTCUSDT", "ETHUSDT"). 거래하려는 암호화폐의 심볼
    """
    try:
        client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)
        positions = client.futures_account()['positions']
        for pos in positions:
            if pos['symbol'] == symbol:
                leverage = int(pos['leverage'])
                return leverage
        return None
    except Exception as e:
        return None

# 코인 종목 레버리지 설정
def set_leverage(symbol, leverage):
    """
    symbol (str): 거래쌍, (예: "BTCUSDT", "ETHUSDT"). 거래하려는 암호화폐의 심볼
    leverage (int): 레버리지 값
    """
    try:
        client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)
        client.futures_change_leverage(symbol=symbol, leverage=int(leverage))
        return True
    except Exception as e:
        return False