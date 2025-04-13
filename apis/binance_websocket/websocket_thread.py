import time
from binance import ThreadedWebsocketManager
from PyQt5.QtCore import QThread, pyqtSignal
import apis.config as c

class BinanceWebsocketThread(QThread):
    # 실시간 현재가
    current_price_received = pyqtSignal(dict)
    # 실시간 주문 체결
    order_filled_received = pyqtSignal(dict)

    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol
        self.twm = None
        self.running = True

    def on_current_price_message(self, msg):
        self.current_price_received.emit(msg)
    
    def on_order_filled_message(self, msg):
        print('sex')
        self.order_filled_received.emit(msg)

    def on_error(self, error):
        print(f'웹소켓 에러 발생: {error}')
        self.reconnect()

    def on_close(self, ws, *args):
        print('웹소켓 연결 종료')
        if self.running:
            print('웹소켓 재연결 시도 중...')
            time.sleep(3)
            self.start()

    def run(self):
        self.twm = ThreadedWebsocketManager(api_key=c.BINANCE_API_KEY, api_secret=c.BINANCE_API_SECRET)
        self.twm.start()
        self.twm.start_symbol_ticker_socket(callback=self.on_current_price_message, symbol=self.symbol)
        self.twm.start_futures_user_socket(callback=self.on_order_filled_message)
        while self.running:
            time.sleep(1)

    def stop(self):
        self.running = False
        if self.twm:
            self.twm.stop()