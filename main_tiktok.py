import logging
from datetime import datetime

from setup import setup
from tiktok import TikTok
from upload_tiktok import UploadTikTok

if __name__ == "__main__":
    start = datetime.now()

    session, logger = setup("id.bungamungil.vtuber-asia-v3.main", logging.INFO)

    tiktok = TikTok(session, logger)
    tiktok_csv = tiktok.create_csv()
    upload_tiktok = UploadTikTok(tiktok_csv, session, logger)
    logger.info(upload_tiktok.upload())
    upload_tiktok.save_on_db()
    del tiktok
    del tiktok_csv
    del upload_tiktok

    del session

    end = datetime.now()

    logger.info(f"Duration: {end - start}")
    del logger
