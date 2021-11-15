from dotenv import load_dotenv


def load_env():
    """
    Loads the .env file and sets the environment variables.
    """
    if load_dotenv() is None:
        raise Exception('Error loading .env file')
    print('Loaded .env file')
