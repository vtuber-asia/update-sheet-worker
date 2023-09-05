import logging
from datetime import datetime

from bilibili import Bilibili
from instagram import Instagram
from setup import setup
from tiktok import TikTok
from twitch import Twitch
from twitter import Twitter
from upload_bilibili import UploadBilibili
from upload_instagram import UploadInstagram
from upload_link import UploadLink
from upload_tiktok import UploadTikTok
from upload_twitch import UploadTwitch
from upload_twitter import UploadTwitter
from upload_youtube import UploadYouTube
from youtube import YouTube

if __name__ == "__main__":
    start = datetime.now()

    session, logger = setup("id.bungamungil.vtuber-asia-v3.main", logging.INFO)

    youTube = YouTube(session, logger)
    youTube_csv = youTube.create_csv()
    upload_youtube = UploadYouTube(youTube_csv, session, logger)
    logger.info(upload_youtube.upload())
    upload_link = UploadLink(youTube_csv, session, logger)
    logger.info(upload_link.upload())
    del youTube
    del youTube_csv
    del upload_youtube
    del upload_link

    twitch = Twitch(session, logger)
    twitch_csv = twitch.create_csv()
    upload_twitch = UploadTwitch(twitch_csv, session, logger)
    logger.info(upload_twitch.upload())
    del twitch
    del twitch_csv
    del upload_twitch

    tiktok = TikTok(session, logger)
    tiktok_csv = tiktok.create_csv()
    upload_tiktok = UploadTikTok(tiktok_csv, session, logger)
    logger.info(upload_tiktok.upload())
    del tiktok
    del tiktok_csv
    del upload_tiktok

    twitter = Twitter(session, logger)
    twitter_csv = twitter.create_csv()
    upload_twitter = UploadTwitter(twitter_csv, session, logger)
    logger.info(upload_twitter.upload())
    del twitter
    del twitter_csv
    del upload_twitter

    bilibili = Bilibili(session, logger)
    bilibili_csv = bilibili.create_csv()
    upload_bilibili = UploadBilibili(bilibili_csv, session, logger)
    logger.info(upload_bilibili.upload())
    del bilibili
    del bilibili_csv
    del upload_bilibili

    instagram = Instagram(session, logger)
    instagram_csv = instagram.create_csv()
    upload_instagram = UploadInstagram(instagram_csv, session, logger)
    logger.info(upload_instagram.upload())
    del instagram
    del instagram_csv
    del upload_instagram

    del session

    end = datetime.now()

    logger.info(f"Duration: {end - start}")
    del logger
