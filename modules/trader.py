import enum
import os
from decimal import Decimal

from binance.client import Client
from dotenv import load_dotenv

from modules.asset import Asset, AssetEncoder
from modules.coin_data import CoinData

_client: Client


def init_trader(testnet):
    if testnet:
        _client = Client(
            os.getenv('BINANCE_API_KEY_TEST'),
            os.getenv('BINANCE_API_SECRET_TEST')
        )
        _client.API_URL = 'https://testnet.binance.vision/api'
    else:
        _client = Client(
            os.getenv('BINANCE_API_KEY_LIVE'),
            os.getenv('BINANCE_API_SECRET_LIVE')
        )


def get_balance(symbol):
    """
    Get the balance of an asset
    """
    return _client.get_asset_balance(symbol)


def get_symbol_ticker(symbol, pairing):
    """
    Get symbol ticker.
    """
    return _client.get_symbol_ticker(symbol+pairing)


def cancel_order(symbol, pairing, order_id):
    """
    Cancel an order.
    """
    return _client.cancel_order(symbol=symbol+pairing, orderId=order_id)


def create_market_order(symbol, pairing, side, quantity):
    """
    Place a market order.
    """
    return _client.create_order(
        symbol=symbol+pairing,
        side=side,
        type=_client.ORDER_TYPE_MARKET,
        quantity=quantity,
    )


def create_limit_order(symbol, pairing, side, quantity, price):
    """
    Place a limit order.
    """
    return _client.order_limit(
        symbol=symbol+pairing,
        side=side,
        quantity=quantity,
        price=price,
    )
