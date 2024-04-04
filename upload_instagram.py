from upload import Upload
from csv import DictReader

from content_platform import ContentPlatform
from instagram import Instagram
import os


class UploadInstagram(Upload):

    def cell_ranges(self) -> list:
        return [
            'Instagram!A3:M',
        ]

    def data_from(self) -> list:
        username = Instagram(self.session, self.logger).fetch_username_cells()
        with open(self.csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv = list(DictReader(csvfile))
            csvfile.close()
        cells = []
        for username in username:
            if username is not None:
                rows = list(filter(lambda row: row['username'].lower() == ContentPlatform.remove_handler_from(
                    username).lower(), from_csv))
                if len(rows) > 0:
                    cells.append(UploadInstagram.map_to_cell_from(rows[0]))
                else:
                    cells.append(['', '', '', '', '', '', '', ''])
            else:
                cells.append(['', '', '', '', '', '', '', ''])
        return [
            {
                'range': 'Summary!BM3:BT',
                'values': cells,
            },
            {
                'range': self.cell_ranges()[0],
                'values': list(map(UploadInstagram.map_to_cell_with_xlookup_from, from_csv))
            }
        ]

    @staticmethod
    def map_to_cell_from(row) -> list:
        return [
            UploadInstagram.cell_username_from(row),
            UploadInstagram.cell_name_from(row),
            UploadInstagram.cell_is_verified_from(row),
            UploadInstagram.cell_profile_image_url_from(row),
            UploadInstagram.cell_followers_count_from(row),
            UploadInstagram.cell_following_count_from(row),
            UploadInstagram.cell_post_count_from(row),
            UploadInstagram.cell_timestamp_from(row),
        ]

    @staticmethod
    def map_to_cell_with_xlookup_from(row) -> list:
        return [
            UploadInstagram.cell_username_from(row),
            UploadInstagram.cell_name_from(row),
            UploadInstagram.cell_profile_image_url_from(row),
            UploadInstagram.cell_followers_count_from(row),
            UploadInstagram.cell_following_count_from(row),
            UploadInstagram.cell_post_count_from(row),
            f'=XLOOKUP("@{
                row["username"]
            }";Summary!$BM$3:$BM;Summary!$B$3:$B)',
            f'=XLOOKUP("@{
                row["username"]
            }";Summary!$BM$3:$BM;Summary!$C$3:$C)',
            f'=XLOOKUP("@{
                row["username"]
            }";Summary!$BM$3:$BM;Summary!$E$3:$E)',
            f'=XLOOKUP("@{
                row["username"]
            }";Summary!$BM$3:$BM;Summary!$F$3:$F)',
            UploadInstagram.cell_is_verified_from(row),
            f'=XLOOKUP("@{
                row["username"]
            }";Summary!$BM$3:$BM;Summary!$D$3:$D)',
            UploadInstagram.cell_timestamp_from(row),
        ]

    @staticmethod
    def cell_username_from(row) -> str:
        if 'username' in row:
            return f'=hyperlink("https://instagram.com/{row["username"]}"; "@{row["username"]}")'
        return ''

    @staticmethod
    def cell_name_from(row) -> str:
        if 'name' in row and 'username' in row:
            return f'=hyperlink("https://instagram.com/{row["username"]}"; "{row["name"]}")'
        return ''

    @staticmethod
    def cell_is_verified_from(row):
        if 'is_verified' in row and row['is_verified'] and row['is_verified'].lower() == 'true':
            return f'=image("{os.getenv("TWITTER_BLUE_BADGE_URL")}"; 4; 20; 20)'
        return ''

    @staticmethod
    def cell_profile_image_url_from(row):
        if 'profile_image_url' in row and row['profile_image_url']:
            return f'=image("{row["profile_image_url"]}")'
        return ''

    @staticmethod
    def cell_followers_count_from(row):
        if 'followers_count' in row:
            return row['followers_count']
        return ''

    @staticmethod
    def cell_following_count_from(row):
        if 'following_count' in row:
            return row['following_count']
        return ''

    @staticmethod
    def cell_post_count_from(row):
        if 'post_count' in row:
            return row['post_count']
        return ''

    @staticmethod
    def cell_timestamp_from(row):
        if 'timestamp' in row:
            return row['timestamp']
        return ''
