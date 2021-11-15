import logging

from dotenv import load_dotenv


def load_env():
    """
    Loads the .env file and sets the environment variables.
    """
    if load_dotenv() is (None or False):
        logging.critical('Error loading .env file!')
        raise Exception('Error loading .env file')
    logging.debug('Loaded .env file')
