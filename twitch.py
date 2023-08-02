import os
from csv import DictReader, DictWriter
from datetime import datetime

from content_platform import ContentPlatform
from gservices import gspread_service
from utils import split


class Twitch(ContentPlatform):

    def fetch_username_cells(self) -> list:
        response = gspread_service().spreadsheets().values().get(
            spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
            range="P3:P",
        ).execute()
        if 'values' in response:
            return list(map(ContentPlatform.cells_on, response['values']))
        return []

    def fetch_user(self, username: str) -> dict | None:
        username = ContentPlatform.remove_handler_from(
            username)  # broadcast_id
        self.logger.info(f"Fetching Twitch channel info for @{username}")
        return self.session.get(
            'https://api.twitch.tv/helix/channels/followers',
            params={
                'broadcaster_id': username
            },
            headers=self.__app_access_headers()
        ).json()

    def create_csv(self) -> str:
        csv_filename = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_twitch.csv'
        fields = [
            'username',
            'broadcast_id',
            'channel_title',
            'profile_image_url',
            'followers_count',
            'timestamp',
        ]
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            slices = split(self.fetch_usernames(), 100)
            for slice in slices:
                fetched = self.__fetch_users(
                    list(map(ContentPlatform.remove_handler_from, slice)))
                for user in fetched['data']:
                    w.writerow({
                        'username': user['login'],
                        'broadcast_id': user['id'],
                        'channel_title': user['display_name'],
                        'profile_image_url': user['profile_image_url'],
                        'followers_count': 0,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
            csvfile.close()
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv_twitch_channels = list(DictReader(csvfile))
            csvfile.close()
        for twitch_channel in from_csv_twitch_channels:
            twitch_channel['followers_count'] = self.fetch_user(
                twitch_channel['broadcast_id'])['total']
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            w.writerows(
                sorted(list(
                    filter(
                        lambda row: row is not None and 'followers_count' in row,
                        from_csv_twitch_channels
                    )
                ), key=lambda row: int(row['followers_count']), reverse=True)
            )
            csvfile.close()
        return csv_filename

    def __fetch_users(self, usernames):
        return self.session.get(
            'https://api.twitch.tv/helix/users',
            params={
                'login': usernames
            },
            headers=self.__app_access_headers()
        ).json()

    def __app_access_headers(self):
        return {
            'Authorization': f'Bearer {self.__app_access_token()}',
            'Client-Id': os.getenv('TWITCH_CLIENT_ID')
        }

    def __app_access_token(self):
        return self.session.post(
            'https://id.twitch.tv/oauth2/token',
            params={
                'client_id': os.getenv('TWITCH_CLIENT_ID'),
                'client_secret': os.getenv('TWITCH_CLIENT_SECRET'),
                'grant_type': 'client_credentials'
            }
        ).json()['access_token']
