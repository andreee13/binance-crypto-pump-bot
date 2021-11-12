import json


class Asset:
    def __init__(self, symbol, amount, orders, stoploss_order):
        self.symbol = symbol
        self.amount = amount
        self.orders = orders
        self.stoploss_order = stoploss_order


class AssetEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__
