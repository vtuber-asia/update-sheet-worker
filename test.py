import logging
from datetime import datetime

from instagram import Instagram
from tiktok import TikTok
from setup import setup

if __name__ == "__main__":
    start = datetime.now()

    session, logger = setup("id.bungamungil.vtuber-asia-v3.main", logging.DEBUG)

    instagram = Instagram(session, logger)
    ig_account = instagram.fetch_user('@kobokanaeru')
    logger.info(ig_account)
    del instagram
    del ig_account

    tiktok = TikTok(session, logger)
    tiktok_account = tiktok.fetch_user('@kobokanaeru')
    logger.info(tiktok_account)
    del tiktok
    del tiktok_account

    del session

    end = datetime.now()

    logger.info(f"Duration: {end - start}")
    del logger
