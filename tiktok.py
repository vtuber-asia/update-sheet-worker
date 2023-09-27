import json
import os
import time
from csv import DictReader, DictWriter
from datetime import datetime

from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from requests.exceptions import ChunkedEncodingError

from content_platform import ContentPlatform
from gservices import gspread_service


class TikTok(ContentPlatform):

    def __init__(self, session, logger):
        super().__init__(session, logger)
        self.setup_browser()

    def __del__(self):
        self.browser.quit()

    def setup_browser(self):
        options = Options()
        options.add_argument("--headless=new")
        self.browser = webdriver.Chrome(options=options)

    def fetch_username_cells(self) -> list:
        response = gspread_service().spreadsheets().values().get(
            spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
            range="Summary!AB3:AB",
        ).execute()
        if 'values' in response:
            return list(map(ContentPlatform.cells_on, response['values']))
        return []

    def fetch_user(self, username: str) -> dict | None:
        username = ContentPlatform.remove_handler_from(username)
        url = f'https://www.tiktok.com/@{username}'
        self.logger.info(f"Fetching TikTok channel info for @{username}")
        try:
            self.browser.get(url)
            contains_data = False
            while not contains_data:
                contains_data = 'SIGI_STATE' in self.browser.page_source
                time.sleep(1)
            tree = html.document_fromstring(self.browser.page_source)
            paths = tree.xpath('//script[@id="SIGI_STATE"]')
            data = json.loads(paths[0].text)
            unique_id = data['UserPage']['uniqueId']
            tiktok_user = {
                'username': username.encode('utf-8').decode('iso-8859-1'),
                'user_id': data['UserModule']['users'][unique_id]['id'],
                'channel_title': data['UserModule']['users'][unique_id]['nickname'].encode('utf-8').decode('iso-8859-1'),
                'is_verified': data['UserModule']['users'][unique_id]['verified'],
                'profile_image_url': data['UserModule']['users'][unique_id]['avatarLarger'],
                'followers_count': data['UserModule']['stats'][unique_id]['followerCount'],
                'following_count': data['UserModule']['stats'][unique_id]['followingCount'],
                'hearts_count': data['UserModule']['stats'][unique_id]['heartCount'],
                'videos_count': data['UserModule']['stats'][unique_id]['videoCount'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return tiktok_user
        except KeyError:
            self.logger.error(f"Couldn't find TikTok channel info for @{username}")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching TikTok channel info for @{username}, code : {e}")
            return None

    def create_csv(self) -> str:
        csv_filename = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_tiktok.csv'
        fields = [
            'username',
            'user_id',
            'channel_title',
            'is_verified',
            'profile_image_url',
            'followers_count',
            'following_count',
            'hearts_count',
            'videos_count',
            'timestamp',
        ]
        with open(csv_filename, 'w', newline='', encoding='iso-8859-1') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            for username in self.fetch_usernames():
                tiktok_user = False
                while tiktok_user is False:
                    tiktok_user = self.fetch_user(username)
                if tiktok_user is not None:
                    w.writerow(tiktok_user)
            csvfile.close()
        with open(csv_filename, 'r', newline='', encoding='iso-8859-1') as csvfile:
            from_csv_tiktok_users = list(DictReader(csvfile))
            csvfile.close()
        with open(csv_filename, 'w', newline='', encoding='iso-8859-1') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            w.writerows(
                sorted(list(
                    filter(lambda row: row is not None,
                           from_csv_tiktok_users
                           )
                ), key=lambda row: int(row['followers_count']), reverse=True)
            )
            csvfile.close()
        return csv_filename
