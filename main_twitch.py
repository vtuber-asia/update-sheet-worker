import logging
from datetime import datetime

from setup import setup
from twitch import Twitch
from upload_twitch import UploadTwitch

if __name__ == "__main__":
    start = datetime.now()

    session, logger = setup("id.bungamungil.vtuber-asia-v3.main", logging.INFO)

    twitch = Twitch(session, logger)
    twitch_csv = twitch.create_csv()
    upload_twitch = UploadTwitch(session, logger)
    logger.info(upload_twitch.upload(twitch_csv))
    del twitch
    del twitch_csv
    del upload_twitch

    del session

    end = datetime.now()

    logger.info(f"Duration: {end - start}")
    del logger
