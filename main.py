import re
import os
import time
from telethon import TelegramClient, events
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

PAIRING = 'BTC'             # Pairing coin in your wallet
BALANCE = 1                 # Pairing coin amount in your wallet
TESTNET = True              # Testing mode to test the bot
SAFE_MODE = True            # Set to True to use 75% of your balance
TIME_TO_WAIT = 5            # Seconds to wait between each buy and sell
CHAT_ID = -1001448562668    # Pump channel Telegram chat ID

MESSAGE_TEMPLATE = 'The coin we have picked to pump today is'

BINANCE_API_KEY_TEST = os.getenv('BINANCE_API_KEY_TEST')
BINANCE_API_SECRET_TEST = os.getenv('BINANCE_API_SECRET_TEST')

BINANCE_API_KEY_LIVE = os.getenv('BINANCE_API_KEY_LIVE')
BINANCE_API_SECRET_LIVE = os.getenv('BINANCE_API_SECRET_LIVE')

TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
TELEGRAM_API_SECRET = os.getenv('TELEGRAM_API_SECRET')

if TESTNET:
    client = Client(BINANCE_API_KEY_TEST, BINANCE_API_SECRET_TEST)
    client.API_URL = 'https://testnet.binance.vision/api'
else:
    client = Client(BINANCE_API_KEY_LIVE, BINANCE_API_SECRET_LIVE)

if SAFE_MODE:
    BALANCE = BALANCE * 0.75

assets = {}


def main():
    with TelegramClient('pump_bot', TELEGRAM_API_KEY, TELEGRAM_API_SECRET) as telegramClient:

        @telegramClient.on(events.NewMessage(incoming=True, pattern=MESSAGE_TEMPLATE, chats=CHAT_ID))
        async def handler(event):
            try:
                coin = re.search('[#]\w+', event.message.text).group(0)[1:].upper()
                print(f'Pump detected on {coin}!')
                buy(coin)
                time.sleep(TIME_TO_WAIT)
                sell(coin)
            except Exception as e:
                print(f'Unexpected error occured. Reason: {e}')    

        telegramClient.run_until_disconnected()


def getAmount(coin):
    print(f'Calculating amount of {coin} to buy...')
    try:
        return round(BALANCE / float(client.get_symbol_ticker(symbol=coin+PAIRING)['price']))
    except Exception as e:
        raise Exception(f'Failed to get {coin} price')


def buy(coin):
    try:
        temp_amount = getAmount(coin)
    except Exception as e:
        print(f'Failed to buy {coin}. Reason: {e}')
        return
    try:
        if coin in assets:
            assets[coin] += temp_amount
        else:
            assets[coin] = temp_amount
        print(f'Buying {assets[coin]} {coin}...')
        order = client.create_order(
            symbol=coin+PAIRING,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=assets[coin],
        )
        print(f'Successfully bought {assets[coin]} {coin}')
    except Exception as e:
        assets[coin] -= temp_amount
        print(f'Failed to buy {coin}. Reason: {e}')


def sell(coin):
    if coin in assets and assets[coin] > 0:
        try:
            print(f'Selling {assets[coin]} {coin}...')
            order = client.create_order(
                symbol=coin+PAIRING,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=assets[coin],
            )
            print(f'Successfully sold {assets[coin]} {coin}')
            assets[coin] = 0
        except Exception as e:
            print(f'Failed to sell {coin} Reason: {e}')
    else:
        print(f'No {coin} to sell')


if __name__ == "__main__":
    main()
