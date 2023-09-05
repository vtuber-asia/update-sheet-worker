from upload import Upload
from csv import DictReader

from content_platform import ContentPlatform
from tiktok import TikTok
from metric_models import TikTokMetric
import uuid
import os


class UploadTikTok(Upload):

    def cell_ranges(self) -> list:
        return [
            'TikTok!A3:O',
        ]

    def data_from(self) -> list:
        usernames = TikTok(self.session, self.logger).fetch_username_cells()
        with open(self.csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv_tiktok_channels = list(DictReader(csvfile))
            csvfile.close()
        cells = []
        for username in usernames:
            if username is not None:
                rows = list(filter(lambda row: row['username'].lower() == ContentPlatform.remove_handler_from(
                    username).lower(), from_csv_tiktok_channels))
                if len(rows) > 0:
                    cells.append(UploadTikTok.map_to_cell_from(rows[0]))
                else:
                    cells.append(['', '', '', '', '', '', '', '', '', ''])
            else:
                cells.append(['', '', '', '', '', '', '', '', '', ''])
        return [
            {
                'range': 'Summary!AC3:AL',
                'values': cells,
            },
            {
                'range': self.cell_ranges()[0],
                'values': list(map(UploadTikTok.map_to_cell_with_xlookup_from, from_csv_tiktok_channels))
            }
        ]
    
    def save_on_db(self):
        with open(self.csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv_tiktok_channels = list(DictReader(csvfile))
            csvfile.close()
        for row in from_csv_tiktok_channels:
            tiktok_metric = TikTokMetric()
            tiktok_metric.id = str(uuid.uuid4())
            tiktok_metric.account_id = row['user_id']
            tiktok_metric.followers_count = row['followers_count']
            tiktok_metric.followings_count = row['following_count']
            tiktok_metric.likes_count = row['hearts_count']
            tiktok_metric.videos_count = row['videos_count']
            tiktok_metric.created_at = f"{row['timestamp']}+{os.getenv('UTC_OFFSET')}"
            tiktok_metric.save(force_insert=True)

    @staticmethod
    def map_to_cell_from(row) -> list:
        return [
            UploadTikTok.cell_username_from(row),
            UploadTikTok.cell_user_id_from(row),
            UploadTikTok.cell_channel_title_from(row),
            UploadTikTok.cell_is_verified_from(row),
            UploadTikTok.cell_profile_image_url_from(row),
            UploadTikTok.cell_followers_count_from(row),
            UploadTikTok.cell_following_count_from(row),
            UploadTikTok.cell_hearts_count_from(row),
            UploadTikTok.cell_videos_count_from(row),
            UploadTikTok.cell_timestamp_from(row),
        ]

    @staticmethod
    def map_to_cell_with_xlookup_from(row) -> list:
        return [
            UploadTikTok.cell_username_from(row),
            UploadTikTok.cell_user_id_from(row),
            UploadTikTok.cell_channel_title_from(row),
            UploadTikTok.cell_profile_image_url_from(row),
            UploadTikTok.cell_followers_count_from(row),
            UploadTikTok.cell_following_count_from(row),
            UploadTikTok.cell_hearts_count_from(row),
            UploadTikTok.cell_videos_count_from(row),
            f'=XLOOKUP("@{row["username"]}";Summary!$AC$3:$AC;Summary!$B$3:$B)',
            f'=XLOOKUP("@{row["username"]}";Summary!$AC$3:$AC;Summary!$C$3:$C)',
            f'=XLOOKUP("@{row["username"]}";Summary!$AC$3:$AC;Summary!$E$3:$E)',
            f'=XLOOKUP("@{row["username"]}";Summary!$AC$3:$AC;Summary!$F$3:$F)',
            UploadTikTok.cell_is_verified_from(row),
            f'=XLOOKUP("@{row["username"]}";Summary!$AC$3:$AC;Summary!$D$3:$D)',
            UploadTikTok.cell_timestamp_from(row),
        ]

    @staticmethod
    def cell_username_from(row):
        if 'username' in row and row['username']:
            return f'=hyperlink("https://tiktok.com/@{row["username"]}"; "@{row["username"]}")'
        return ''
    
    @staticmethod
    def cell_user_id_from(row):
        if 'user_id' in row:
            return row['user_id']
        return ''

    @staticmethod
    def cell_channel_title_from(row):
        if 'channel_title' in row and row['channel_title'] and 'username' in row and row['username']:
            return f'=hyperlink("https://tiktok.com/@{row["username"]}"; "{row["channel_title"]}")'
        return ''
    
    @staticmethod
    def cell_is_verified_from(row):
        if 'is_verified' in row and row['is_verified'].lower() == 'true':
            return f'=image("{os.getenv("TIKTOK_VERIFIED_URL")}"; 4; 20; 20)'
        return ''
    
    @staticmethod
    def cell_profile_image_url_from(row):
        if 'profile_image_url' in row:
            return f'=image("{row["profile_image_url"]}"; 4; 80; 80)'
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
    def cell_hearts_count_from(row):
        if 'hearts_count' in row:
            return row['hearts_count']
        return ''
    
    @staticmethod
    def cell_videos_count_from(row):
        if 'videos_count' in row:
            return row['videos_count']
        return ''

    @staticmethod
    def cell_timestamp_from(row):
        if 'timestamp' in row:
            return row['timestamp']
        return ''

    