import json


class AssetEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def dump_all_assets(assets):
    """
    Dumps all assets to a json file.
    """
    logging.info('Dumping assets...')
    file_name = f'assets/"ASSETS"_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
    with open(file_name, 'w') as f:
        json.dump(assets, f, cls=AssetEncoder, indent=2)
        logging.info(f'Dumped assets to {file_name}')


def dump_asset(asset):
    """
    Dumps an asset to a json file.
    """
    logging.info(f'Dumping asset {asset.name}...')
    file_name = f'assets/"{asset}"_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
    with open(file_name, 'w') as f:
        json.dump(asset, f, cls=AssetEncoder, indent=2)
        logging.info(f'Dumped asset {asset} to {file_name}')
