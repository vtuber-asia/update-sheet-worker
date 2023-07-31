from dotenv import load_dotenv
from youtube import update_youtube_channels
import logging


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    print(update_youtube_channels())
