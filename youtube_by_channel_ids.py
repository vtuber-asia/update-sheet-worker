from youtube import YouTube
from datetime import datetime
from csv import DictReader, DictWriter
from gservices import gspread_service
import os
from content_platform import ContentPlatform
from utils import split


class YouTubeByChannelIds(YouTube):

    def fetch_channel_id_cells(self) -> list:
        response = gspread_service().spreadsheets().values().get(
            spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
            range="Summary!I3:I"
        ).execute()
        if 'values' in response:
            return list(map(ContentPlatform.cells_on, response['values']))
        return []

    def fetch_channel_ids(self) -> list:
        return list(
            filter(
                lambda channel_id: channel_id is not None,
                self.fetch_channel_id_cells()
            )
        )

    def create_csv(self) -> str:
        csv_filename = f'./outputs/{
            datetime.now().strftime("%Y%m%d%H%M%S")
        }_youtube_by_cid.csv'
        fields = [
            'username',
            'channel_id',
            'channel_title',
            'badges',
            'is_membership_active',
            'profile_image_url',
            'banner_image_url',
            'videos_count',
            'views_count',
            'subscribers_count',
            'username_twitch',
            'username_tiktok',
            'username_twitter',
            'username_bstation',
            'timestamp'
        ]
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            youtube_channel_ids_chunks = split(self.fetch_channel_ids(), 50)
            for youtube_channel_ids_chunk in youtube_channel_ids_chunks:
                from_api_youtube_channels = self.from_api_fetch_channels_for(
                    youtube_channel_ids_chunk
                )['items']
                for from_api_youtube_channel in from_api_youtube_channels:
                    w.writerow({
                        'username': ContentPlatform.remove_handler_from(from_api_youtube_channel['snippet']['customUrl']) if 'customUrl' in from_api_youtube_channel['snippet'] else None,
                        'channel_id': from_api_youtube_channel['id'],
                        'channel_title': from_api_youtube_channel['snippet']['title'],
                        'badges': None,
                        'is_membership_active': None,
                        'profile_image_url': YouTube.from_api_thumbnail(from_api_youtube_channel),
                        'banner_image_url': YouTube.from_api_banner(from_api_youtube_channel),
                        'videos_count': YouTube.from_api_videos_count(from_api_youtube_channel),
                        'views_count': YouTube.from_api_views_count(from_api_youtube_channel),
                        'subscribers_count': YouTube.from_api_subscribers_count(from_api_youtube_channel),
                        'username_twitch': None,
                        'username_tiktok': None,
                        'username_twitter': None,
                        'username_bstation': None,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
            csvfile.close()
        with open(csv_filename, 'r', newline='', encoding='iso-8859-1') as csvfile:
            from_csv_youtube_channels = list(DictReader(csvfile))
            csvfile.close()
        with open(csv_filename, 'w', newline='', encoding='iso-8859-1') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            w.writerows(
                sorted(list(
                    filter(
                        lambda row: row is not None and 'subscribers_count' in row,
                        from_csv_youtube_channels
                    )
                ), key=lambda row: int(row['subscribers_count']), reverse=True)
            )
            csvfile.close()
        return csv_filename
