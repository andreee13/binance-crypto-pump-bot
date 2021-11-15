import json


class AssetEncoder(json.JSONEncoder):
    """
    :param asset: Asset
    """

    def default(self, o):
        return o.__dict__


class Asset:
    """
    :param symbol: str
    :param amount: Decimal
    :param orders: list of Order
    :param stoploss_order: Order
    """

    def __init__(self, symbol, amount, orders, stoploss_order):
        self.symbol = symbol
        self.amount = amount
        self.orders = orders
        self.stoploss_order = stoploss_order
