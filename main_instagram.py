import logging
from datetime import datetime

from instagram import Instagram
from setup import setup
from upload_instagram import UploadInstagram

if __name__ == "__main__":
    start = datetime.now()

    session, logger = setup("id.bungamungil.vtuber-asia-v3.main", logging.INFO)

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
