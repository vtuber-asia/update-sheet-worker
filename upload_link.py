from csv import DictReader
from os import getenv
from content_platform import ContentPlatform
from upload import Upload
from youtube import YouTube
from gservices import gspread_service


class UploadLink(Upload):

    def cell_ranges(self) -> list:
        return [
            getenv('GOOGLE_SHEET_RANGE_FOR_TWITCH_URL_FROM_YOUTUBE'),
            getenv('GOOGLE_SHEET_RANGE_FOR_TIKTOK_URL_FROM_YOUTUBE'),
            getenv('GOOGLE_SHEET_RANGE_FOR_BILIBILI_URL_FROM_YOUTUBE'),
            getenv('GOOGLE_SHEET_RANGE_FOR_TWITTER_URL_FROM_YOUTUBE'),
            getenv('GOOGLE_SHEET_RANGE_FOR_INSTAGRAM_URL_FROM_YOUTUBE'),
        ]

    def data_from(self) -> list:
        usernames = YouTube(self.session, self.logger).fetch_username_cells()
        with open(self.csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv_youtube_channels = list(DictReader(csvfile))
            csvfile.close()
        twitch_usernames = []
        tiktok_usernames = []
        twitter_usernames = []
        bilibili_usernames = []
        instagram_usernames = []
        for username in usernames:
            if username is not None:
                rows = list(filter(lambda row: row['username'] == ContentPlatform.remove_handler_from(
                    username), from_csv_youtube_channels))
                if len(rows) > 0:
                    twitch_usernames.append(rows[0])
                    tiktok_usernames.append(rows[0])
                    twitter_usernames.append(rows[0])
                    bilibili_usernames.append(rows[0])
                    instagram_usernames.append(rows[0])
                else:
                    twitch_usernames.append('')
                    tiktok_usernames.append('')
                    twitter_usernames.append('')
                    bilibili_usernames.append('')
                    instagram_usernames.append('')
            else:
                twitch_usernames.append('')
                tiktok_usernames.append('')
                twitter_usernames.append('')
                bilibili_usernames.append('')
                instagram_usernames.append('')
        return [
            {
                'range': self.cell_ranges()[0],
                'values': list(map(lambda username: [UploadLink.cell_username_twitch_from(username)], twitch_usernames))
            },
            {
                'range': self.cell_ranges()[1],
                'values': list(map(lambda username: [UploadLink.cell_username_tiktok_from(username)], tiktok_usernames))
            },
            {
                'range': self.cell_ranges()[2],
                'values': list(map(lambda username: [UploadLink.cell_username_bilibili_from(username)], twitter_usernames))
            },
            {
                'range': self.cell_ranges()[3],
                'values': list(map(lambda username: [UploadLink.cell_username_twitter_from(username)], bilibili_usernames))
            },
            {
                'range': self.cell_ranges()[4],
                'values': list(map(lambda username: [UploadLink.cell_username_instagram_from(username)], instagram_usernames))
            }
        ]

    def upload(self):
        self.logger.info(f"Uploading {self.csv_filename} to Google Sheet ...")
        data = self.data_from()
        if self.is_empty_data(data):
            return f"Data on {self.csv_filename} is empty, upload canceled."
        self.clear_data_on_sheet()
        return gspread_service().spreadsheets().values().batchUpdate(
            spreadsheetId=getenv("GOOGLE_SHEET_ID_SRC"),
            body={
                'valueInputOption': 'USER_ENTERED',
                'data': data,
            },
        ).execute()

    def clear_data_on_sheet(self):
        return gspread_service().spreadsheets().values().batchClear(
            spreadsheetId=getenv("GOOGLE_SHEET_ID_SRC"),
            body={
                'ranges': self.cell_ranges(),
            },
        ).execute()

    @staticmethod
    def cell_username_twitch_from(row):
        if 'username_twitch' in row and row['username_twitch']:
            return f'=hyperlink("https://twitch.tv/{row["username_twitch"]}"; "@{row["username_twitch"]}")'
        return ''

    @staticmethod
    def cell_username_tiktok_from(row):
        if 'username_tiktok' in row and row['username_tiktok']:
            return f'=hyperlink("https://tiktok.com/@{row["username_tiktok"]}"; "@{row["username_tiktok"]}")'
        return ''

    @staticmethod
    def cell_username_bilibili_from(row):
        if 'username_bstation' in row and row['username_bstation']:
            return f'=hyperlink("https://www.bilibili.tv/en/space/{row["username_bstation"]}"; "@{row["username_bstation"]}")'
        return ''

    @staticmethod
    def cell_username_twitter_from(row):
        if 'username_twitter' in row and row['username_twitter']:
            return f'=hyperlink("https://twitter.com/{row["username_twitter"]}"; "@{row["username_twitter"]}")'
        return ''

    @staticmethod
    def cell_username_instagram_from(row):
        if 'username_instagram' in row and row['username_instagram']:
            return f'=hyperlink("https://instagram.com/{row["username_instagram"]}"; "@{row["username_instagram"]}")'
        return ''
