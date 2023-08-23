import logging
from datetime import datetime

from bilibili import Bilibili
from setup import setup
from upload_bilibili import UploadBilibili

if __name__ == "__main__":
    start = datetime.now()

    session, logger = setup("id.bungamungil.vtuber-asia-v3.main", logging.INFO)

    bilibili = Bilibili(session, logger)
    bilibili_csv = bilibili.create_csv()
    upload_bilibili = UploadBilibili(session, logger)
    logger.info(upload_bilibili.upload(bilibili_csv))
    del bilibili
    del bilibili_csv
    del upload_bilibili

    del session

    end = datetime.now()

    logger.info(f"Duration: {end - start}")
    del logger
