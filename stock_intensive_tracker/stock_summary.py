from __future__ import annotations


class StockSummary:

    def __init__(self, stock_code, date, volume, px, perf, trade):
        self.stock_code = stock_code
        self.date = date
        self.volume = volume
        self.px = px
        self.perf = perf
        self.trade = trade

