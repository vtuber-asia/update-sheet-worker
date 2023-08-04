import logging
from logging import Logger

from dotenv import load_dotenv
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def setup(package_name: str, log_level: int) -> (Session, Logger):
    load_dotenv()
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(package_name)
    session = Session()
    retry = Retry(connect=10, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session, logger
