class CoinData:
    """
    :param symbol: str
    :param price: Decimal
    :param amount: float
    """

    def __init__(self, symbol, price, amount):
        self.symbol = symbol
        self.price = price
        self.amount = amount
