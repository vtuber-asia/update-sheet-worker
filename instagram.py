import os
import time
from csv import DictReader, DictWriter
from datetime import datetime
from json import loads
from logging import Logger

from requests import Session

from content_platform import ContentPlatform
from gservices import gspread_service


class Instagram(ContentPlatform):

    def __init__(self, session: Session, logger: Logger):
        super().__init__(session, logger)

    def fetch_username_cells(self) -> list:
        response = gspread_service().spreadsheets().values().get(
            spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
            range="Summary!BL3:BL"
        ).execute()
        if 'values' in response:
            return list(map(ContentPlatform.cells_on, response['values']))
        return []

    def fetch_user(self, username: str) -> dict | None:
        return self.__fetch_user(username, 10)
    
    def __fetch_user(self, username: str, try_left: int) -> dict | None:
        if try_left == 0:
            return None
        username = ContentPlatform.remove_handler_from(username)
        self.logger.info(f"Fetching Instagram user info for @{username}")
        try:
            response = self.session.get(
                os.getenv('IG_API_ENDPOINT'),
                headers={
                    'X-Ig-App-Id': os.getenv('IG_APP_ID'),
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': '*/*'
                },
                params={
                    'username': username,
                }
            )
            json = loads(response.text)
            if 'status' in json and json['status'].lower() == 'ok' and 'data' in json and 'user' in json['data']:
                json_data = json['data']['user']
                return {
                    'username': username,
                    'name': Instagram.name_from(json_data),
                    'is_verified': Instagram.has_blue_checkmark_from(json_data),
                    'profile_image_url': Instagram.profile_image_from(json_data),
                    'followers_count': Instagram.followers_count_from(json_data),
                    'following_count': Instagram.following_count_from(json_data),
                    'post_count': Instagram.post_count_from(json_data),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
        except Exception as e:
            self.logger.error(
                f"Error fetching Instagram account info for @{username}: {e}, retrying ...")
            time.sleep(2)
            return self.fetch_user(username, try_left - 1)
        return None

    def create_csv(self) -> str:
        csv_filename = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_instagram.csv'
        fields = [
            'username',
            'name',
            'is_verified',
            'profile_image_url',
            'followers_count',
            'following_count',
            'post_count',
            'timestamp',
        ]
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields)
            w.writeheader()
            for username in self.fetch_usernames():
                user = self.fetch_user(username)
                if user is not None:
                    w.writerow(user)
            csvfile.close()
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv = list(DictReader(csvfile))
            csvfile.close()
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields)
            w.writeheader()
            w.writerows(
                sorted(list(
                    filter(lambda row: row is not None, from_csv)
                ), key=lambda row: int(row['followers_count']), reverse=True)
            )
            csvfile.close()
        return csv_filename

    @staticmethod
    def name_from(json_data) -> str:
        if 'full_name' in json_data:
            return json_data['full_name']
        return ''

    @staticmethod
    def has_blue_checkmark_from(json_data) -> bool:
        if 'is_verified' in json_data:
            return json_data['is_verified']
        return False

    @staticmethod
    def profile_image_from(json_data) -> str:
        if 'profile_pic_url' in json_data:
            return json_data['profile_pic_url']
        return ''

    @staticmethod
    def followers_count_from(json_data) -> int:
        if 'edge_followed_by' in json_data and 'count' in json_data['edge_followed_by']:
            return json_data['edge_followed_by']['count']
        return 0

    @staticmethod
    def following_count_from(json_data) -> int:
        if 'edge_follow' in json_data and 'count' in json_data['edge_follow']:
            return json_data['edge_follow']['count']
        return 0

    @staticmethod
    def post_count_from(json_data) -> int:
        if 'edge_owner_to_timeline_media' in json_data and 'count' in json_data['edge_owner_to_timeline_media']:
            return json_data['edge_owner_to_timeline_media']['count']
        return 0
