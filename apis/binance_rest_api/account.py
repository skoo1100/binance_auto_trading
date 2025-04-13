import pandas as pd
from binance.client import Client
import apis.config as c

# 현물 계좌정보
def get_account():
    client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)

    account_info = client.get_account()
    
    # 매도, 매수, 구매자, 판매자 수수료
    maker_commission = account_info['makerCommission']
    taker_commission = account_info['takerCommission']
    buyer_commission = account_info['buyerCommission']
    seller_commission = account_info['sellerCommission']

    # commissionRates: maker, taker, buyer, seller의 수수료 dict
    commission_rates = account_info['commissionRates']
    maker = commission_rates['maker']
    taker = commission_rates['taker']
    buyer = commission_rates['buyer']
    seller = commission_rates['seller']

    # bool 여부
    bool_trade = account_info['canTrade']    # 거래 가능 여부
    bool_withdraw = account_info['canWithdraw']  # 계좌 출금 여부
    bool_deposit = account_info['canDeposit']    # 계좌입금 여부
    bool_brokered = account_info['brokered']     # 중개인 관리 여부
    bool_require_self_trade_prevention = account_info['requireSelfTradePrevention']  # 자기 거래 방지 여부
    bool_prevent_sor = account_info['preventSor']    # 특정 종류의 거래 제한이 있는지 여부

    # 계좌 정보가 마지막으로 업데이트된 시간 (밀리초)
    update_time = account_info['updateTime']

    # 계좌 유형 (spot, margin)
    account_type = account_info['accountType']

    # 자산 정보 (asset: 유형, free: 출금 가능 잔고, locked: 잠금 상태 잔고)
    balances = account_info['balances']
    balances_df = pd.DataFrame(balances)

    return {
        'maker_commission': maker_commission,
        'taker_commission': taker_commission,
        'buyer_commission': buyer_commission,
        'seller_commission': seller_commission,
        'commission_rates': {
            'maker': maker,
            'taker': taker,
            'buyer': buyer,
            'seller': seller
        },
        'bool_trade': bool_trade,
        'bool_withdraw': bool_withdraw,
        'bool_deposit': bool_deposit,
        'bool_brokered': bool_brokered,
        'bool_require_self_trade_prevention': bool_require_self_trade_prevention,
        'bool_prevent_sor': bool_prevent_sor,
        'update_time': update_time,
        'account_type': account_type,
        'balances': balances_df
    }

# 선물 계좌정보
def get_future_account():
    client = Client(c.BINANCE_API_KEY, c.BINANCE_API_SECRET)

    # 선물 계좌 정보 가져오기
    futures_account_info = client.futures_account()

    # 선물 계좌에서 사용 가능한 데이터들
    total_wallet_balance = futures_account_info.get('totalWalletBalance', 0.0)  # 전체 지갑 잔고
    total_unrealized_profit = futures_account_info.get('totalUnrealizedProfit', 0.0)  # 미실현 손익
    total_margin_balance = futures_account_info.get('totalMarginBalance', 0.0)  # 총 마진 잔고
    total_position_margin = futures_account_info.get('totalPositionMargin', 0.0)  # 포지션 마진 (없으면 0.0)
    available_balance = futures_account_info.get('availableBalance', 0.0)  # 사용 가능한 잔고
    assets = futures_account_info.get('assets', [])  # 자산 목록

    # 선물 계좌에서 포지션 정보 가져오기
    positions = futures_account_info['positions']  # 선물 포지션 목록
    positions_df = pd.DataFrame(positions)

    return {
        'total_wallet_balance': total_wallet_balance,
        'total_unrealized_profit': total_unrealized_profit,
        'total_margin_balance': total_margin_balance,
        'total_position_margin': total_position_margin,
        'available_balance': available_balance,
        'assets': assets,
        'positions': positions_df
    }