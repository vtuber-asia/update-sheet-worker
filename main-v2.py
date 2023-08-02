from dotenv import load_dotenv
from requests import Session
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from youtube import YouTube
from twitch import Twitch
from tiktok import TikTok
import logging


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("id.bungamungil")
    session = Session()
    retry = Retry(connect=10, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    youTube = YouTube(session, logger)
    csv = youTube.create_csv()
    twitch = Twitch(session, logger)
    csv = twitch.create_csv()
    tiktok = TikTok(session, logger)
    csv = tiktok.create_csv()
    print(csv)
    
