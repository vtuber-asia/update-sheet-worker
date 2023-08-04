import logging

from bilibili import Bilibili
from setup import setup
from tiktok import TikTok
from twitch import Twitch
from twitter import Twitter
from upload_bilibili import UploadBilibili
from upload_link import UploadLink
from upload_tiktok import UploadTikTok
from upload_twitch import UploadTwitch
from upload_twitter import UploadTwitter
from upload_youtube import UploadYouTube
from youtube import YouTube


if __name__ == "__main__":
    session, logger = setup("id.bungamungil.vtuber-asia-v3.main", logging.INFO)

    youTube = YouTube(session, logger)
    youTube_csv = youTube.create_csv()
    upload_youtube = UploadYouTube(session, logger)
    logger.info(upload_youtube.upload(youTube_csv))
    upload_link = UploadLink(session, logger)
    logger.info(upload_link.upload(youTube_csv))

    twitch = Twitch(session, logger)
    twitch_csv = twitch.create_csv()
    upload_twitch = UploadTwitch(session, logger)
    logger.info(upload_twitch.upload(twitch_csv))

    tiktok = TikTok(session, logger)
    tiktok_csv = tiktok.create_csv()
    upload_tiktok = UploadTikTok(session, logger)
    logger.info(upload_tiktok.upload(tiktok_csv))

    twitter = Twitter(session, logger)
    twitter_csv = twitter.create_csv()
    upload_twitter = UploadTwitter(session, logger)
    logger.info(upload_twitter.upload(twitter_csv))

    bilibili = Bilibili(session, logger)
    bilibili_csv = bilibili.create_csv()
    upload_bilibili = UploadBilibili(session, logger)
    logger.info(upload_bilibili.upload(bilibili_csv))
