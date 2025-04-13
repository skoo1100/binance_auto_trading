from datetime import datetime
from apis.binance_rest_api.historic_data import get_historic_data
from apis.binance_websocket.websocket_thread import BinanceWebsocketThread
from components.trade import TradeClass

class WebSocketClass:
    def __init__(self, main_window):
        self.main_window = main_window
        self.ws_binance_thread = None
        self.trade_class = TradeClass(self)
    
    # 웹소켓 시작
    def start_websocket(self):
        self.ws_binance_thread = BinanceWebsocketThread(self.main_window.market_name)
        self.ws_binance_thread.current_price_received.connect(lambda data: self.update_current_price_market(data, self.main_window.market_name))
        self.ws_binance_thread.order_filled_received.connect(lambda data: self.update_check_order_filled(data))
        self.ws_binance_thread.start()
    
    # 웹소켓 중지
    def stop_websocket(self):
        if self.ws_binance_thread and self.ws_binance_thread.isRunning():
            self.ws_binance_thread.stop()

    # 현재가 업데이트
    def update_current_price_market(self, data, symbol):
        """
        data:
        {
            "e" 이벤트 유형 (24시간 티커 업데이트)
            "E" 이벤트 발생 시간 (Unix Timestamp, 밀리초)
            "s" 거래 심볼 (비트코인/USDT)
            "p" 가격 변동 (24시간 동안)
            "P" 가격 변동률 (%)  
            "w" 24시간 거래량 가중 평균 가격
            "x" 24시간 전 가격 (전일 종가)
            "c" 현재 가격 (마지막 체결 가격)
            "Q" 마지막 체결 수량
            "b" 최우선 매수 가격 (현재 최고 매수 호가)
            "B" 최우선 매수 호가의 수량
            "a" 최우선 매도 가격 (현재 최저 매도 호가)
            "A" 최우선 매도 호가의 수량
            "o" 24시간 전 가격 (전일 종가와 동일)
            "h" 24시간 동안의 최고가
            "l" 24시간 동안의 최저가
            "v" 24시간 동안의 거래량 (symbol = BTCUSDT일 때 BTC 기준)
            "q" 24시간 동안의 거래량 (symbol = BTCUSDT일 때 USDT 기준)
            "O" 24시간 전 타임스탬프
            "C" 이벤트 발생 타임스탬프
            "F" 첫 번째 거래 ID
            "L" 마지막 거래 ID
            "n" 거래 개수 (지난 24시간 동안)
        }
        """
        self.update_current_coin_data_list(data)
        # 실시간 현재가 출력
        format_time = datetime.fromtimestamp(data["E"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        current_price = float(data['c']) 
        self.main_window.current_price_log.append(f"[{format_time}] 현재가: {current_price} {symbol}")
        # 1000줄 이상이면 1000줄까지만 나오도록 하기
        while self.main_window.current_price_log.document().blockCount() > 1000:
            cursor = self.main_window.current_price_log.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.NextBlock, cursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()

    # 코인 데이터 업데이트
    def update_current_coin_data_list(self, new_data):
        if self.main_window.current_coin_data_list:
            if (new_data['E'] - self.main_window.current_coin_data_list[-1]['timestamp'] >= 1000 * 60 * 5):
                self.main_window.current_coin_data_list.append({
                    "timestamp": new_data["E"],
                    "high": new_data["h"],
                    "low": new_data["l"],
                    "close": new_data["c"]
                })
                # 코인 데이터 업데이트시 거래 ㄱㄱ
                self.trade_class.trade_stocks()
                # 계좌 정보와 코인 정보 업데이트
                self.main_window.update_class.update_main_account_and_coin()
                # 메모리 관리 (총 25시간 데이터)
                if len(self.main_window.current_coin_data_list) > 600:
                    self.main_window.current_coin_data_list.pop(0)
            else:
                return None
        else:
            for item in get_historic_data(symbol=self.main_window.market_name, interval="5m"):
                self.main_window.current_coin_data_list.append({
                    "timestamp": item['timestamp'],
                    "high": float(item['high']),
                    "low": float(item['low']),
                    "close": float(item['close'])
                })

    def update_check_order_filled(self, data):
        """
        "e": "executionReport",      # 이벤트 타입
        "E": 1672500000000,          # 이벤트 시간 (timestamp)
        "s": "BTCUSDT",              # 심볼
        "c": "myOrder123",           # 클라이언트 지정 주문 ID
        "S": "BUY",                  # 주문 방향 (BUY / SELL)
        "o": "LIMIT",                # 주문 타입 (LIMIT, MARKET 등)
        "f": "GTC",                  # 주문 유효 시간 (GTC 등)
        "q": "0.001",                # 주문 수량
        "p": "21000.00",             # 주문 가격
        "x": "TRADE",                # 주문 상태 업데이트 유형
        "X": "FILLED",              # 주문 상태 (PARTIALLY_FILLED, FILLED 등)
        "r": "NONE",                # 거부 이유
        "i": 1234567890,            # Binance 시스템 내 주문 ID
        "l": "0.001",               # 직전 체결 수량
        "z": "0.001",               # 누적 체결 수량
        "L": "20999.99",            # 직전 체결 가격
        "n": "0.02",                # 수수료 금액
        "N": "BNB",                 # 수수료 자산
        "T": 1672500000001,         # 체결 시간
        "m": False,                 # 메이커 여부
        "M": True,                  # 격리 마진 여부
        "R": False,                 # 리듀스 온리 여부
        "wt": "CONTRACT_PRICE",     # 주문 트리거 조건
        "ot": "LIMIT",              # 오리지널 주문 타입
        "ps": "BOTH",               # 포지션 사이드 (롱, 숏, 양방향)
        "cp": False,                # 조건부 주문
        """
        # 주문 체결 되었을때 매매 로그 남기기
        if data.get('X') == 'FILLED':
            format_time = datetime.fromtimestamp(data["E"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            symbol = data['s']
            buysell = '매수' if data['S'] == 'BUY' else '매도'
            quantity = data['q']
            price = data['p']
            self.main_window.buysell_log.append(f"[{format_time}] [{symbol}: {buysell}] 수량: [{quantity}], 구매 가격: [{price}]")