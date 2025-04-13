from PyQt5.QtCore import QTime
from apis.binance_rest_api.account import get_future_account
from apis.binance_rest_api.commision import get_future_commission
from apis.binance_rest_api.market import get_market_limits
from apis.binance_rest_api.order_futures import *
from utils.round import round_value
from utils.trading_strategy import *

class TradeClass:
    def __init__(self, web_socket_class):
        self.main_window = web_socket_class.main_window

    def trade_stocks(self):
        if not self.main_window.current_coin_data_list:
            return
        
        # 기존 주문 취소
        close_futures_orders(self.main_window.market_name)
        
        # 자릿수
        _, tick_size = self.limit_market_data()
        
        # 현재가 풀매수 변수
        price = self.trade_price(tick_size)
        quantity = self.trade_full_balance_quantity(price)

        # 1. 현재 포지션 확인
        direction = get_direction(self.main_window.market_name)

        # 2. 트레이딩 전략 설정
        selected_strategy = self.main_window.trading_strategy_combo_box.currentText()
        print(selected_strategy)
        if selected_strategy == "RSI":
            signal = rsi_strategy(self.main_window.current_coin_data_list)
        elif selected_strategy == "MACD":
            signal = macd_strategy(self.main_window.current_coin_data_list)
        elif selected_strategy == "Triple RSI":
            signal = triple_rsi_strategy(self.main_window.current_coin_data_list)
        else:
            signal = None
        
        # 3. 자동매매 진행
        # 포지션 진입: 현재 포지션이 없을 때 (FLAT)
        if direction == "FLAT":
            if signal == "BUY":
                print("롱 포지션 진입!")
                order_futures_limit(self.main_window.market_name, "BUY", quantity, price)  # 매수 주문
            elif signal == "SELL":
                print("숏 포지션 진입!")
                order_futures_limit(self.main_window.market_name, "SELL", quantity, price)  # 매도 주문
        # 롱 포지션 (Long)일 때, TP, SL 설정
        elif direction == "LONG":
            entry_price, tp_price, sl_price, position_amt= calculate_tp_sl(self.main_window.market_name, 1.2, 1.0, direction, tick_size)
            if tp_price and position_amt and float(price) >= float(entry_price):
                place_tp_order(self.main_window.market_name, tp_price, position_amt, direction)  # TP 주문
            if sl_price and position_amt and float(price) < float(entry_price):
                place_sl_order(self.main_window.market_name, sl_price, position_amt, direction)  # SL 주문

        # 숏 포지션 (Short)일 때, TP, SL 설정
        elif direction == "SHORT":
            entry_price, tp_price, sl_price, position_amt= calculate_tp_sl(self.main_window.market_name, 1.2, 1.0, direction, tick_size)
            if tp_price and position_amt and float(price) <= float(entry_price):
                place_tp_order(self.main_window.market_name, tp_price, position_amt, direction)  # TP 주문
                self.main_window.buysell_log.append(f"[{QTime.currentTime().toString('HH:mm:ss')}] 숏 포지션 청산 (매수)")
            if sl_price and position_amt and float(price) > float(entry_price):
                place_sl_order(self.main_window.market_name, sl_price, position_amt, direction)  # SL 주문
                self.main_window.buysell_log.append(f"[{QTime.currentTime().toString('HH:mm:ss')}] 숏 포지션 손절 (매수)")

    def trade_full_balance_quantity(self, price):
        # 수수료
        fee_rate = get_future_commission(self.main_window.market_name)
        # 계좌 잔액
        account_data = get_future_account()
        available_balance = float(account_data['available_balance'])
        # 계산
        calculate_balance = available_balance  * (1 + float(fee_rate['maker_commission'])) / float(price)
        quantity = round_value(calculate_balance, 1)
        return quantity
    
    def trade_price(self, tick_size):
        latest_data = self.main_window.current_coin_data_list[-1]
        latest_price = float(latest_data["close"])
        tick_size_price = round_value(latest_price, tick_size)
        return tick_size_price
    
    def limit_market_data(self):
        market_limit = get_market_limits(self.main_window.market_name)
        step_size = market_limit['step_size']   # 수량 단위 자릿수
        tick_size = market_limit['tick_size']   # 주문 가격 단위 자릿수
        return step_size, tick_size