import logging
from datetime import datetime

from setup import setup
from twitter import Twitter
from upload_twitter import UploadTwitter

if __name__ == "__main__":
    start = datetime.now()

    session, logger = setup("id.bungamungil.vtuber-asia-v3.main", logging.INFO)

    twitter = Twitter(session, logger)
    twitter_csv = twitter.create_csv()
    upload_twitter = UploadTwitter(twitter_csv, session, logger)
    logger.info(upload_twitter.upload())
    upload_twitter.save_on_db()
    del twitter
    del twitter_csv
    del upload_twitter

    del session

    end = datetime.now()

    logger.info(f"Duration: {end - start}")
    del logger
