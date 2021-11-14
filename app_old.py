import json
import logging
import os
import re
import signal
import sys
import time
from datetime import datetime
from decimal import Decimal

from binance.client import Client
from dotenv import load_dotenv
from telethon import TelegramClient, events

from modules.asset import Asset, AssetEncoder
from modules.coin_data import CoinData

PAIRING = 'BTC'             # Pairing coin in your wallet
BALANCE = 1                 # Pairing coin amount in your wallet
TESTNET = True              # Testing mode to test the bot
SAFE_MODE = True            # Set to True to use 75% of your balance
TIME_TO_WAIT = 10           # Seconds to wait between each buy and sell
STOPLOSS = 0.9              # Stoploss percentage. Set to 0 to disable
CHAT_ID = -1001448562668    # Pump channel Telegram chat ID

MESSAGE_TEMPLATE = 'The coin we have picked to pump today is'

load_dotenv()

TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')

BINANCE_API_KEY_TEST = os.getenv('BINANCE_API_KEY_TEST')
BINANCE_API_SECRET_TEST = os.getenv('BINANCE_API_SECRET_TEST')

BINANCE_API_KEY_LIVE = os.getenv('BINANCE_API_KEY_LIVE')
BINANCE_API_SECRET_LIVE = os.getenv('BINANCE_API_SECRET_LIVE')

if TESTNET:
    client = Client(BINANCE_API_KEY_TEST, BINANCE_API_SECRET_TEST)
    client.API_URL = 'https://testnet.binance.vision/api'
else:
    client = Client(BINANCE_API_KEY_LIVE, BINANCE_API_SECRET_LIVE)

if SAFE_MODE:
    BALANCE = float(BALANCE * 0.75)

ASSETS = {}


def main():
    logging.basicConfig(level=logging.INFO, filename=f'logs/log_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log',
                        filemode='w', format="%(asctime)-15s %(levelname)-8s %(message)s")
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info('Starting bot...')
    signal.signal(signal.SIGINT, signal_handler)
    with TelegramClient('logs/telegram', TELEGRAM_API_ID, TELEGRAM_API_HASH) as telegramClient:

        @telegramClient.on(events.NewMessage(incoming=True, pattern=MESSAGE_TEMPLATE, chats=CHAT_ID))
        async def handler(event):
            handlePumpSignal(event.message.text)

        logging.info('Bot started!')
        telegramClient.run_until_disconnected()


def signal_handler(signal, frame):
    logging.info('Exiting...')
    dumpAssets()
    logging.info('Exited!')
    sys.exit(0)


def handlePumpSignal(message):
    try:
        coin = re.search('[#]\w+', message).group(0)[1:].upper()
        logging.info(f'Pump detected on {coin}!')
        buy(coin)
        logging.info(f'Waiting {TIME_TO_WAIT} seconds...')
        time.sleep(TIME_TO_WAIT)
        sell(coin)
        logging.info(f'Pump finished on {coin}!')
        dumpAssets(coin)
    except Exception as e:
        logging.critical(f'Unexpected error occured: {e}')


def dumpAssets(coin: str = None):
    if (coin is None and len(ASSETS) > 0) or (coin is not None and coin in ASSETS):
        try:
            file_name = f'assets/{"assets" if coin is None else coin}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
            logging.info('Dumping assets...')
            out_file = open(file_name, 'w')
            json.dump(
                ASSETS if coin is None else ASSETS[coin], out_file, cls=AssetEncoder, indent=2)
            logging.info(f'Assets dumped to {file_name}')
        except Exception as e:
            logging.error(f'Failed to dump assets. Reason: {e}')
    else:
        logging.info(f'No assets to dump!')


def getCoinData(coin):
    logging.info(f'Getting {coin} data...')
    try:
        price = client.get_symbol_ticker(symbol=coin+PAIRING)['price']
        return CoinData(coin, Decimal(price), round(BALANCE / float(price)))
    except Exception as e:
        raise Exception(f'Error getting {coin} data: {e}')


def buy(coin):
    try:
        coin_data = getCoinData(coin)
        logging.info(f'Data retrieved for {coin}')
    except Exception as e:
        logging.error(f'Failed to buy {coin}. Reason: {e}')
        return
    try:
        logging.info(
            f'Buying {coin_data.amount} {coin} at {coin_data.price} {PAIRING}...')
        buy_order = client.create_order(
            symbol=coin+PAIRING,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=coin_data.amount,
        )
        if coin in ASSETS:
            ASSETS[coin].amount += coin_data.amount
            ASSETS[coin].orders.append(buy_order)
        else:
            ASSETS[coin] = Asset(coin, coin_data.amount,
                                 [buy_order], None)
        if STOPLOSS > 0:
            try:
                logging.info(f'Placing {coin} stoploss order...')
                stoploss_order = client.order_limit_sell(
                    symbol=coin+PAIRING,
                    quantity=coin_data.amount,
                    price=Decimal(round(coin_data.price*Decimal(STOPLOSS), 6)),
                )
                ASSETS[coin].stoploss_order = stoploss_order
                logging.info(f'{coin} stoploss order placed')
            except Exception as e:
                raise Exception(f'Error placing {coin} stoploss order: {e}')
        logging.info(f'Successfully bought {coin_data.amount} {coin}')
    except Exception as e:
        logging.error(f'Failed to buy {coin}. Reason: {e}')


def sell(coin):
    if coin in ASSETS and ASSETS[coin].amount > 0:
        try:
            logging.info(
                f'Selling {ASSETS[coin].amount} {coin} to {PAIRING}...')
            sell_order = client.create_order(
                symbol=coin+PAIRING,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=ASSETS[coin].amount,
            )
            logging.info(f'Successfully sold {ASSETS[coin].amount} {coin}')
            ASSETS[coin].amount = 0
            ASSETS[coin].orders.append(sell_order)
            if ASSETS[coin].stoploss_order is not None:
                try:
                    logging.info(f'Cancelling {coin} stoploss order...')
                    client.cancel_order(
                        symbol=coin+PAIRING,
                        orderId=ASSETS[coin].stoploss_order['orderId'],
                    )
                    logging.info(f'{coin} stoploss order cancelled')
                except Exception as e:
                    logging.warning(
                        f'Failed to cancel {coin} stoploss order. Reason: {e}')
        except Exception as e:
            logging.error(f'Failed to sell {coin} Reason: {e}')
    else:
        logging.warning(f'No {coin} to sell')


if __name__ == "__main__":
    main()
