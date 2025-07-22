# looger.py
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(log_config):
    name = log_config.get("name")
    log_file = log_config.get("log_file")
    level_str = log_config.get("level", "INFO").upper()
    max_bytes = log_config.get("max_bytes", 10 * 1024 * 1024)
    backup_count = log_config.get("backup_count", 3)

    level = getattr(logging, level_str, logging.INFO)
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        logger.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )

        fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = False
    return logger
