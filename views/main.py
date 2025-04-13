import math
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from apis.binance_rest_api.account import get_future_account
from apis.binance_rest_api.leverage import get_leverage, set_leverage
from apis.binance_rest_api.market import get_all_market
from components.update import UpdateClass
from components.websocket import WebSocketClass

form_class = uic.loadUiType("ui/main.ui")[0]

class Main(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        """ 변수들 """
        # 코인 이름
        self.market_name = ''
        # 코인 현재가 리스트
        self.current_coin_data_list = []
        # 코인 종목 리스트
        self.market_data = []
        # 계좌 정보 리스트
        self.account_data = []
        # 검색 리스트
        self.all_account_coin_list = []
        self.all_binance_coin_list = []
        self.current_coin_list = []

        """ 컴포넌트 """
        self.websocket_class = WebSocketClass(self)
        self.update_class = UpdateClass(self)

        """ 불러오기 """
        self.update_class.update_main_account_and_coin()

        """ Pyqt5 위젯"""
        # 코인 검색
        self.search_coin_input.textChanged.connect(lambda: self.search_coin_list(self.current_coin_list))
        # 코인 리스트 버튼
        self.all_coin_button.setEnabled(False)
        self.account_coin_button.setEnabled(True)
        self.all_coin_button.clicked.connect(lambda: self.on_coin_list_button_click('binance'))
        self.account_coin_button.clicked.connect(lambda: self.on_coin_list_button_click('account'))
        self.coin_list.itemClicked.connect(self.on_coin_item_click)
        # 거래 타이머 시작/중지 버튼의 클릭 이벤트 연결
        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(False)
        self.button_start.clicked.connect(self.start_trading)
        self.button_stop.clicked.connect(self.stop_trading)
        # 레버리지 스핀 박스
        self.leverage_spin_box.setEnabled(False)
        self.leverage_spin_box.valueChanged.connect(lambda value: self.get_leverage_data(self.market_name, value))

        """ 타이머 """
        # 거래 타이머
        self.trade_timer = QTimer()
        #self.trade_timer.timeout.connect(self.trade_class.trade_stocks)

    def start_trading(self):
        #self.trade_timer.start(1000 * 60 * 5)
        self.websocket_class.start_websocket()
        # 버튼 설정
        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)
        self.coin_list.itemClicked.disconnect(self.on_coin_item_click)
        self.leverage_spin_box.setEnabled(False)
        self.trading_strategy_combo_box.setEnabled(False)
    
    def stop_trading(self):
        #self.trade_timer.stop()
        self.websocket_class.stop_websocket()
        self.current_coin_data_list.clear()
        # 버튼 설정
        self.button_start.setEnabled(True)
        self.button_stop.setEnabled(False)
        self.coin_list.itemClicked.connect(self.on_coin_item_click)
        self.leverage_spin_box.setEnabled(True)
        self.trading_strategy_combo_box.setEnabled(True)

    def get_leverage_data(self, symbol, value = 1):
        set_leverage(symbol, value)
        leverage = get_leverage(symbol)
        if leverage is None:
            self.leverage_spin_box.setValue(0)
            self.button_start.setEnabled(False)
            return False
        else:
            self.leverage_spin_box.setValue(int(leverage))
            self.button_start.setEnabled(True)
            return True

    def search_coin_list(self, select_coin_list):
        search_text = self.search_coin_input.text().lower()
        self.coin_list.clear()
        if not search_text:
            for coin in select_coin_list:
                self.coin_list.addItem(coin)
            return
        for coin in select_coin_list:
            if search_text in coin.lower():
                self.coin_list.addItem(coin)

    def on_coin_list_button_click(self, type):
        if type == 'binance':
            self.all_coin_button.setEnabled(False)
            self.account_coin_button.setEnabled(True)
            self.search_coin_input.setText('')
            self.coin_list.clear()
            self.coin_list.addItems(self.all_binance_coin_list)
            self.current_coin_list = self.all_binance_coin_list
        if type == 'account':
            self.all_coin_button.setEnabled(True)
            self.account_coin_button.setEnabled(False)
            self.search_coin_input.setText('')
            self.coin_list.clear()
            self.coin_list.addItems(self.all_account_coin_list)
            self.current_coin_list = self.all_account_coin_list

    def on_coin_item_click(self, item):
        coin_text = item.text()
        coin_name = coin_text.split(":")[0]
        self.market_name = coin_name
        self.coin_input.setText(coin_name)
        # 레버리지 설정
        if self.leverage_spin_box.isEnabled() is False:
            self.leverage_spin_box.setEnabled(True)
        get_leverage = self.get_leverage_data(self.market_name)
        # 시작 버튼 활성화
        if self.coin_input and get_leverage:
            self.button_start.setEnabled(True)
        else:
            self.button_start.setEnabled(False)