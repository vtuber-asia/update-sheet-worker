import logging
from datetime import datetime

from instagram import Instagram
from setup import setup
from upload_instagram import UploadInstagram

if __name__ == "__main__":
    start = datetime.now()

    session, logger = setup("id.bungamungil.vtuber-asia-v3.main", logging.DEBUG)

    instagram = Instagram(session, logger)
    ig_account = instagram.fetch_user('@kobokanaeru')
    logger.info(ig_account)
    del instagram

    del session

    end = datetime.now()

    logger.info(f"Duration: {end - start}")
    del logger
