from __future__ import annotations

from datetime import datetime
import json


class StockSummary:

    def __init__(self, stock_code: str, date: datetime, volume: int, price: int, performance: float, trade: int):
        self.stock_code: str = stock_code
        self.date: datetime = date
        self.volume: int = volume
        self.price: int = price
        self.performance: float = performance
        self.trade: int = trade

    def __str__(self):
        return f'StockSummary(stock_code={ self.stock_code}, date={self.date}, volume={self.volume}, ' \
               f'price={self.price}, performance={self.performance}, trade={self.trade})'

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
