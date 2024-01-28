from upload import Upload
from csv import DictReader
from content_platform import ContentPlatform
from twitch import Twitch
from account_models import TwitchAccount
from metric_models import TwitchMetric
import uuid
from os import getenv


class UploadTwitch(Upload):

    def data_from(self) -> list:
        usernames = Twitch(self.session, self.logger).fetch_username_cells()
        with open(self.csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv_twitch_channels = list(DictReader(csvfile))
            csvfile.close()
        cells = []
        for username in usernames:
            if username is not None:
                rows = list(filter(lambda row: row['username'].lower() == ContentPlatform.remove_handler_from(
                    username).lower(), from_csv_twitch_channels))
                if len(rows) > 0:
                    cells.append(UploadTwitch.map_to_cell_from(rows[0]))
                else:
                    cells.append(['', '', '', '', '', ''])
            else:
                cells.append(['', '', '', '', '', ''])
        return [
            {
                'range': getenv('GOOGLE_SHEET_RANGE_SRC_DATA'),
                'values': cells,
            },
            {
                'range': self.cell_ranges()[0],
                'values': list(map(UploadTwitch.map_to_cell_with_xlookup_from, from_csv_twitch_channels))
            }
        ]

    def save_on_db(self):
        with open(self.csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv_twitch_channels = list(DictReader(csvfile))
            csvfile.close()
        for row in from_csv_twitch_channels:
            twitch_metric = TwitchMetric()
            twitch_metric.id = str(uuid.uuid4())
            twitch_metric.account_id = row['broadcast_id']
            twitch_metric.followers_count = row['followers_count']
            twitch_metric.created_at = f"{row['timestamp']}{getenv('UTC_OFFSET')}"
            twitch_metric.save(force_insert=True)
            twitch_account = TwitchAccount()
            twitch_account.insert(
                account_id=row['broadcast_id'],
                username=row['username'],
                title=row['channel_title'],
                profile_image_url=row['profile_image_url'],
                created_at=f"{row['timestamp']}{getenv('UTC_OFFSET')}",
                updated_at=f"{row['timestamp']}{getenv('UTC_OFFSET')}",
                id=str(uuid.uuid4()),
            ).on_conflict(
                preserve=[
                    TwitchAccount.username, 
                    TwitchAccount.title, 
                    TwitchAccount.profile_image_url,
                    TwitchAccount.updated_at
                ],
            ).execute()

    @staticmethod
    def map_to_cell_from(row) -> list:
        return [
            UploadTwitch.cell_username_from(row),
            UploadTwitch.cell_broadcast_id_from(row),
            UploadTwitch.cell_channel_title_from(row),
            UploadTwitch.cell_profile_image_url_from(row),
            UploadTwitch.cell_followers_count_from(row),
            UploadTwitch.cell_timestamp_from(row),
        ]

    @staticmethod
    def map_to_cell_with_xlookup_from(row) -> list:
        return [
            UploadTwitch.cell_username_from(row),
            UploadTwitch.cell_broadcast_id_from(row),
            UploadTwitch.cell_channel_title_from(row),
            UploadTwitch.cell_profile_image_url_from(row),
            UploadTwitch.cell_followers_count_from(row),
            f'=XLOOKUP("@{row["username"]}";Profile!$G$3:$G;Profile!$B$3:$B)',
            f'=XLOOKUP("@{row["username"]}";Profile!$G$3:$G;Profile!$C$3:$C)',
            f'=XLOOKUP("@{row["username"]}";Profile!$G$3:$G;Profile!$E$3:$E)',
            f'=XLOOKUP(XLOOKUP("@{row["username"]}";Profile!$G$3:$G;Profile!$E$3:$E);Groups!$C$3:$C;Groups!$B$3:$B)',
            f'=XLOOKUP("@{row["username"]}";Profile!$G$3:$G;Profile!$D$3:$D)',
            UploadTwitch.cell_timestamp_from(row),
        ]

    @staticmethod
    def cell_username_from(row):
        if 'username' in row and row['username']:
            return f'=hyperlink("https://twitch.tv/{row["username"].lower()}"; "@{row["username"].lower()}")'
        return ''

    @staticmethod
    def cell_broadcast_id_from(row):
        if 'broadcast_id' in row:
            return row['broadcast_id']
        return ''

    @staticmethod
    def cell_channel_title_from(row):
        if 'channel_title' in row and row['channel_title'] and 'username' in row and row['username']:
            return f'=hyperlink("https://twitch.tv/{row["username"].lower()}"; "{row["channel_title"]}")'
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
    def cell_timestamp_from(row):
        if 'timestamp' in row:
            return row['timestamp']
        return ''
