import logging
from datetime import datetime

from setup import setup
from upload_link import UploadLink
from upload_youtube import UploadYouTube
from youtube_by_channel_ids import YouTubeByChannelIds

if __name__ == "__main__":
    start = datetime.now()

    session, logger = setup("id.bungamungil.vtuber-asia-v3.main", logging.INFO)

    youTube = YouTubeByChannelIds(session, logger)
    youTube_csv = youTube.create_csv()
    upload_youtube = UploadYouTube(youTube_csv, session, logger)
    logger.info(upload_youtube.upload())
    upload_link = UploadLink(youTube_csv, session, logger)
    logger.info(upload_link.upload())
    del youTube
    del youTube_csv
    del upload_youtube
    del upload_link

    del session

    end = datetime.now()

    logger.info(f"Duration: {end - start}")
    del logger
