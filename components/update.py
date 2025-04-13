from apis.binance_rest_api.account import get_future_account
from apis.binance_rest_api.market import get_all_market

class UpdateClass:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def update_main_account_and_coin(self):
        # 계좌 정보 갱신
        self.main_window.account_data = get_future_account()
        self.main_window.label_account.setText(f'계좌 잔액: {self.main_window.account_data['available_balance']} USDT')
        # 코인 정보 갱신
        self.main_window.market_data = get_all_market()
        # 검색 리스트 갱신
        self.main_window.all_account_coin_list = self.main_window.account_data['positions'][['symbol', 'positionAmt', 'entryPrice']].apply(
            lambda row: f"{row['symbol']}: {float(row['positionAmt']) * float(row['entryPrice'])}", axis=1
        ).tolist()
        self.main_window.all_binance_coin_list = self.main_window.market_data[self.main_window.market_data['orderTypes'].apply(
            lambda x: 'LIMIT' in x
        )]['symbol'].tolist()
        if self.main_window.all_coin_button.isEnabled():
            self.main_window.current_coin_list = self.main_window.all_binance_coin_list
        else:
            self.main_window.current_coin_list = self.main_window.all_account_coin_list
        self.main_window.coin_list.addItems(self.main_window.current_coin_list)

