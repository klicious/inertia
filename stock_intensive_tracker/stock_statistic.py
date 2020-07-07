from __future__ import annotations


class StockStatistic:

    def __init__(self, stock_code, date, share_price, daily_price_change, buy_participation_ratio, t_3_pref,
                 buy_execution, market_buy_volume):
        self.stock_code = stock_code
        self.date = date
        self.share_price = share_price
        self.daily_price_change = daily_price_change
        self.buy_participation_ratio = buy_participation_ratio
        self.t_3_pref = t_3_pref
        self.buy_execution = buy_execution
        self.market_buy_volume = market_buy_volume
