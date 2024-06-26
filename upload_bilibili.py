from upload import Upload
from csv import DictReader

from content_platform import ContentPlatform
from bilibili import Bilibili
from os import getenv


class UploadBilibili(Upload):

    def data_from(self) -> list:
        username = Bilibili(self.session, self.logger).fetch_username_cells()
        with open(self.csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv_bilibili_channels = list(DictReader(csvfile))
            csvfile.close()
        cells = []
        for username in username:
            if username is not None:
                rows = list(filter(lambda row: row['user_id'].lower() == ContentPlatform.remove_handler_from(
                    username).lower(), from_csv_bilibili_channels))
                if len(rows) > 0:
                    cells.append(UploadBilibili.map_to_cell_from(rows[0]))
                else:
                    cells.append(['', '', '', '', '', '', '', ''])
            else:
                cells.append(['', '', '', '', '', '', '', ''])
        return [
            {
                'range': getenv('GOOGLE_SHEET_RANGE_SRC_DATA'),
                'values': cells,
            },
            {
                'range': self.cell_ranges()[0],
                'values': list(map(UploadBilibili.map_to_cell_with_xlookup_from, from_csv_bilibili_channels))
            }
        ]

    @staticmethod
    def map_to_cell_from(row) -> list:
        return [
            UploadBilibili.cell_username_from(row),
            UploadBilibili.cell_channel_title_from(row),
            UploadBilibili.cell_is_verified_from(row),
            UploadBilibili.cell_profile_image_url_from(row),
            UploadBilibili.cell_followers_count_from(row),
            UploadBilibili.cell_following_count_from(row),
            UploadBilibili.cell_likes_count_from(row),
            UploadBilibili.cell_timestamp_from(row),
        ]

    @staticmethod
    def map_to_cell_with_xlookup_from(row) -> list:
        return [
            UploadBilibili.cell_username_from(row),
            UploadBilibili.cell_channel_title_from(row),
            UploadBilibili.cell_profile_image_url_from(row),
            UploadBilibili.cell_followers_count_from(row),
            UploadBilibili.cell_following_count_from(row),
            UploadBilibili.cell_likes_count_from(row),
            f'=XLOOKUP("@{row["user_id"]}";Profile!$I$3:$I;Profile!$B$3:$B)',
            f'=XLOOKUP("@{row["user_id"]}";Profile!$I$3:$I;Profile!$C$3:$C)',
            f'=XLOOKUP("@{row["user_id"]}";Profile!$I$3:$I;Profile!$E$3:$E)',
            f'=XLOOKUP(XLOOKUP("@{
                row["user_id"]
            }";Profile!$I$3:$I;Profile!$E$3:$E);Groups!$C$3:$C;Groups!$B$3:$B)',
            UploadBilibili.cell_is_verified_from(row),
            f'=XLOOKUP("@{row["user_id"]}";Profile!$I$3:$I;Profile!$D$3:$D)',
            UploadBilibili.cell_timestamp_from(row),
        ]

    @staticmethod
    def cell_username_from(row):
        if 'user_id' in row and row['user_id']:
            return f'=hyperlink("https://www.bilibili.tv/en/space/{row["user_id"]}"; "@{row["user_id"]}")'
        return ''

    @staticmethod
    def cell_channel_title_from(row):
        if 'channel_title' in row and row['channel_title'] and 'user_id' in row and row['user_id']:
            return f'=hyperlink("https://www.bilibili.tv/en/space/{row["user_id"]}"; "{row["channel_title"]}")'
        return ''

    @staticmethod
    def cell_is_verified_from(row):
        if 'is_verified' in row and row['is_verified'] and row['is_verified'].lower() == 'true':
            return f'=image("{getenv("BILIBILI_VERIFIED_URL")}"; 4; 20; 20)'
        return ''

    @staticmethod
    def cell_profile_image_url_from(row):
        if 'profile_image_url' in row and row['profile_image_url']:
            return f'=image("{row["profile_image_url"]}"; 4; 80; 80)'
        return ''

    @staticmethod
    def cell_followers_count_from(row):
        if 'followers_count' in row and row['followers_count']:
            return row['followers_count']
        return ''

    @staticmethod
    def cell_following_count_from(row):
        if 'following_count' in row and row['following_count']:
            return row['following_count']
        return ''

    @staticmethod
    def cell_likes_count_from(row):
        if 'likes_count' in row and row['likes_count']:
            return row['likes_count']
        return ''

    @staticmethod
    def cell_timestamp_from(row):
        if 'timestamp' in row and row['timestamp']:
            return row['timestamp']
        return ''
