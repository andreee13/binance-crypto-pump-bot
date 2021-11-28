from datetime import datetime
import json
import logging
import os

from modules.asset import AssetEncoder


def create_directories_structure():
    """
    Creates the directories structure.
    """
    if not os.path.exists('assets'):
        os.makedirs('assets')
    if not os.path.exists('logs'):
        os.makedirs('logs')


def dump_all_assets(assets):
    """
    Dumps all assets to a json file.
    :param assets: dict
    """
    if len(assets) > 0:
        logging.debug('Dumping all assets...')
        file_name = f'assets/ASSETS_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
        logging.debug(f'Creating file {file_name}')
        with open(file_name, 'w') as f:
            logging.debug(f'File {file_name} created')
            json.dump(assets, f, cls=AssetEncoder, indent=2)
            logging.info(f'Dumped assets to {file_name}')
    else:
        logging.info('No assets to dump!')


def dump_asset(asset):
    """
    Dumps an asset to a json file.
    :param asset: Asset
    """
    if asset is not None:
        logging.debug(f'Dumping asset {asset.symbol}...')
        file_name = f'assets/{asset.symbol}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
        logging.debug(f'Creating file {file_name}')
        with open(file_name, 'w') as f:
            logging.debug(f'File {file_name} created')
            json.dump(asset, f, cls=AssetEncoder, indent=2)
            logging.info(f'Dumped asset {asset.symbol} to {file_name}')
    else:
        logging.info('No asset to dump!')
