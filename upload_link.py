from csv import DictReader

from content_platform import ContentPlatform
from upload import Upload
from youtube import YouTube


class UploadLink(Upload):

    def cell_ranges(self) -> list:
        return [
            'Summary!R3:R',
            'Summary!Y3:Y',
            'Summary!AJ3:AJ',
        ]

    def data_from(self, csv_filename) -> list:
        usernames = YouTube(self.session, self.logger).fetch_username_cells()
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv_youtube_channels = list(DictReader(csvfile))
            csvfile.close()
        twitch_usernames = []
        tiktok_usernames = []
        twitter_usernames = []
        for username in usernames:
            if username is not None:
                rows = list(filter(lambda row: row['username'] == ContentPlatform.remove_handler_from(
                    username), from_csv_youtube_channels))
                if len(rows) > 0:
                    twitch_usernames.append(rows[0])
                    tiktok_usernames.append(rows[0])
                    twitter_usernames.append(rows[0])
                else:
                    twitch_usernames.append('')
                    tiktok_usernames.append('')
                    twitter_usernames.append('')
            else:
                twitch_usernames.append('')
                tiktok_usernames.append('')
                twitter_usernames.append('')
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
                'values': list(map(lambda username: [UploadLink.cell_username_twitter_from(username)], twitter_usernames))
            }
        ]

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
    def cell_username_twitter_from(row):
        if 'username_twitter' in row and row['username_twitter']:
            return f'=hyperlink("https://twitter.com/{row["username_twitter"]}"; "@{row["username_twitter"]}")'
        return ''