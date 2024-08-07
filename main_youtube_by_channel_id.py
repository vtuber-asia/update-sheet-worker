import logging
from datetime import datetime

from setup import setup
from upload_youtube_by_channel_ids import UploadYouTubeByChannelIds
from youtube_by_channel_ids import YouTubeByChannelIds

if __name__ == "__main__":
    start = datetime.now()

    session, logger = setup("id.bungamungil.vtuber-asia-v3.main", logging.INFO)

    youTube = YouTubeByChannelIds(session, logger)
    youTube_csv = youTube.create_csv()
    upload_youtube = UploadYouTubeByChannelIds(youTube_csv, session, logger)
    logger.info(upload_youtube.upload())
    del youTube
    del youTube_csv
    del upload_youtube

    del session

    end = datetime.now()

    logger.info(f"Duration: {end - start}")
    del logger
