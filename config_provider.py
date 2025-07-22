# config_provider.py
from config import Config

CONFIG_PATH = "config.yaml"
_config = Config(CONFIG_PATH)


def get_config():
    return _config


def get_logger_name():
    return _config.get_logger_name()
