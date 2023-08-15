import json
import os
from csv import DictReader, DictWriter
from datetime import datetime

from lxml import html
from requests.exceptions import ChunkedEncodingError

from content_platform import ContentPlatform
from gservices import gspread_service


class TikTok(ContentPlatform):

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
            page = self.session.get(url, allow_redirects=False)
            if page.status_code != 200:
                return None
            tree = html.document_fromstring(page.content.decode(encoding='iso-8859-1'))
            paths = tree.xpath('//script[@id="SIGI_STATE"]')
            data = json.loads(paths[0].text)
            unique_id = data['UserPage']['uniqueId']
            tiktok_user = {
                'username': username,
                'user_id': data['UserModule']['users'][unique_id]['id'],
                'channel_title': data['UserModule']['users'][unique_id]['nickname'],
                'is_verified': data['UserModule']['users'][unique_id]['verified'],
                'profile_image_url': data['UserModule']['users'][unique_id]['avatarLarger'],
                'followers_count': data['UserModule']['stats'][unique_id]['followerCount'],
                'following_count': data['UserModule']['stats'][unique_id]['followingCount'],
                'hearts_count': data['UserModule']['stats'][unique_id]['heartCount'],
                'videos_count': data['UserModule']['stats'][unique_id]['videoCount'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return tiktok_user
        except ChunkedEncodingError:
            return self.fetch_user(username)
        except Exception as e:
            self.logger.error(f"Error fetching TikTok channel info for @{username}: {e}")
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
