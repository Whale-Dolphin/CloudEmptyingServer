import logging
import time

def setup_logging(log_level):
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

def get_timestamp():
    return int(time.time())