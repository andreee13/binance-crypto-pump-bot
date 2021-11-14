from dotenv import load_dotenv


def load_env(debug=False):
    load_dotenv(dotenv_path='../.env_debug' if debug else '../.env')
