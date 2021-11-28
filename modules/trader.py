import enum
import os
import logging
import threading

from binance.client import Client
from dotenv import load_dotenv

from modules.asset import Asset, AssetEncoder
from modules.coin_data import CoinData


def init(pairing, quantity, testnet):
    """
    :param testnet: bool
    """
    logging.debug('Initializing Binance client...')
    global _client
    if testnet:
        logging.debug('Using testnet Binance client')
        logging.warning('Running in TEST mode, all trades are simulated!')
        _client = Client(
            os.getenv('BINANCE_API_KEY_TEST'),
            os.getenv('BINANCE_API_SECRET_TEST')
        )
        _client.API_URL = 'https://testnet.binance.vision/api'
    else:
        logging.debug('Using mainnet Binance client')
        logging.warning('Running in LIVE mode, use with caution!')
        _client = Client(
            os.getenv('BINANCE_API_KEY_LIVE'),
            os.getenv('BINANCE_API_SECRET_LIVE')
        )
    _init_periodic_pairing_balance_check(pairing, quantity)
    logging.debug('Binance client initialized')


def _init_periodic_pairing_balance_check(pairing, quantity):
    """
    Initialize periodic balance check.
    :param symbol: str
    """
    threading.Timer(300, _check_symbol_balance(pairing, quantity))
    logging.debug('Periodic balance check initialized')


def _check_symbol_balance(symbol, quantity):
    """
    Check the balance of the pairing.
    :param pairing: str
    """
    logging.debug(f'Checking balance of pairing {symbol}...')
    try:
        if float(get_balance(symbol)['free']) >= quantity:
            logging.info(f'Pairing {symbol} balance is enough')
        else:
            logging.warning(f'Pairing {symbol} balance is not enough!')
    except Exception as e:
        logging.error(f'Error checking pairing balance: {e}')


def get_balance(symbol):
    """
    Get the balance of an asset
    :param symbol: str
    :return: API response
    """
    return _client.get_asset_balance(symbol)


def get_last_price(symbol, pairing):
    """
    Get symbol ticker.
    :param symbol: str
    :param pairing: str
    :return: API response
    """
    return _client.get_symbol_ticker(symbol=symbol+pairing)['price']


def cancel_order(symbol, pairing, order_id):
    """
    Cancel an order.
    :param symbol: str
    :param pairing: str
    :param order_id: str
    :return: API response
    """
    return _client.cancel_order(symbol=symbol+pairing, orderId=order_id)


def create_market_order(symbol, pairing, side, quantity):
    """
    Place a market order.
    :param symbol: str
    :param pairing: str
    :param side: str
    :param quantity: float
    :return: API response
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
    :param symbol: str
    :param pairing: str
    :param side: str
    :param quantity: float
    :param price: float
    :return: API response
    """
    return _client.order_limit(
        symbol=symbol+pairing,
        side=side,
        quantity=quantity,
        price=price,
    )
