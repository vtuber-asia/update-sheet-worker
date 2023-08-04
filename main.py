from dotenv import load_dotenv
from requests import Session
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from youtube import YouTube
from twitch import Twitch
from tiktok import TikTok
from twitter import Twitter
from upload_youtube import UploadYouTube
from upload_link import UploadLink
from upload_twitch import UploadTwitch
from upload_tiktok import UploadTikTok
from upload_twitter import UploadTwitter
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
    # youTube = YouTube(session, logger)
    # csv_filename = youTube.create_csv()
    # upload_youtube = UploadYouTube(session, logger)
    # response = upload_youtube.upload("20230803102150_youtube.csv")
    # upload_link = UploadLink(session, logger)
    # response = upload_link.upload("20230803102150_youtube.csv")
    # upload_twitch = UploadTwitch(session, logger)
    # response = upload_twitch.upload("20230802165249_twitch.csv")
    upload_tiktok = UploadTikTok(session, logger)
    response = upload_tiktok.upload("20230802165427_tiktok.csv")
    twitter = Twitter(session, logger)
    csv = twitter.create_csv()
    upload_twitter = UploadTwitter(session, logger)
    response = upload_twitter.upload(csv)
    print(response)
    # twitch = Twitch(session, logger)
    # csv = twitch.create_csv()
    # tiktok = TikTok(session, logger)
    # csv = tiktok.create_csv()
    # twitter = Twitter(session, logger)
    # csv = twitter.create_csv()
    
