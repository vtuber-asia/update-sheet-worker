import logging
from logging import Logger

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def setup(package_name: str, log_level: int) -> (Session, Logger):
    logging.basicConfig(
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=log_level
    )
    logger = logging.getLogger(package_name)
    session = Session()
    session.headers["User-Agent"] = "RapidAPI/4.2.0 (Macintosh; OS X/14.2.1) GCDHTTPRequest"
    retry = Retry(connect=10, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session, logger
