import json
import os
from csv import DictReader, DictWriter
from datetime import datetime

from lxml import html

from content_platform import ContentPlatform
from gservices import gspread_service, youtube_service
from utils import split


class YouTube(ContentPlatform):

    def fetch_username_cells(self) -> list:
        response = gspread_service().spreadsheets().values().get(
            spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
            range="G3:G"
        ).execute()
        if 'values' in response:
            return list(map(ContentPlatform.cells_on, response['values']))
        return []

    def fetch_user(self, username: str) -> dict | None:
        username = ContentPlatform.remove_handler_from(username)
        url = f'https://www.youtube.com/@{username}'
        self.logger.info(f'Fetching YouTube channel info for @{username} ...')
        youtube_channel = self.__youtube_channel_from_url(url)
        if youtube_channel is None:
            self.logger.warning(f'Could not find YouTube channel: @{username}')
            return None
        links = YouTube.links_on(youtube_channel)
        twitch_links = list(
            filter(lambda link: link['platform'] == 'Twitch', links))
        tiktok_links = list(
            filter(lambda link: link['platform'] == 'TikTok', links))
        twitter_links = list(
            filter(lambda link: link['platform'] == 'Twitter', links))
        bstation_links = list(
            filter(lambda link: link['platform'] == 'Bstation', links))
        return {
            'username': username,
            'channel_id': YouTube.channel_id_on(youtube_channel),
            'channel_title': YouTube.channel_title_on(youtube_channel),
            'badges': YouTube.badges_on(youtube_channel),
            'is_membership_active': YouTube.is_membership_active_on(youtube_channel),
            'profile_image_url': YouTube.profile_image_url_on(youtube_channel),
            'banner_image_url': YouTube.banner_image_url_on(youtube_channel),
            'videos_count': 0,
            'views_count': 0,
            'subscribers_count': 0,
            'username_twitch': twitch_links[0]['username'] if len(twitch_links) > 0 else None,
            'username_tiktok': tiktok_links[0]['username'] if len(tiktok_links) > 0 else None,
            'username_twitter': twitter_links[0]['username'] if len(twitter_links) > 0 else None,
            'username_bstation': bstation_links[0]['username'] if len(bstation_links) > 0 else None,
        }

    def create_csv(self) -> str:
        csv_filename = f'{datetime.now().strftime("%Y%m%d%H%M%S")}_youtube.csv'
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
        with open(csv_filename, 'w', newline='', encoding='iso-8859-1') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            for username in self.fetch_usernames():
                youtube_channel = self.fetch_user(username)
                if youtube_channel is not None:
                    w.writerow(youtube_channel)
            csvfile.close()
        with open(csv_filename, 'r', newline='', encoding='iso-8859-1') as csvfile:
            from_csv_youtube_channels = list(DictReader(csvfile))
            youtube_channel_ids = list(
                map(lambda row: row['channel_id'], list(
                    filter(lambda row: row is not None,
                           from_csv_youtube_channels))
                    )
            )
            csvfile.close()
        youtube_channel_ids_chunks = split(youtube_channel_ids, 50)
        for youtube_channel_ids_chunk in youtube_channel_ids_chunks:
            from_api_youtube_channels = YouTube.from_api_fetch_channels_for(
                youtube_channel_ids_chunk)
            for from_api_youtube_channel in from_api_youtube_channels['items']:
                for from_csv_youtube_channel in from_csv_youtube_channels:
                    if from_api_youtube_channel['id'] == from_csv_youtube_channel['channel_id']:
                        from_csv_youtube_channel['profile_image_url'] = YouTube.from_api_thumbnail(
                            from_api_youtube_channel)
                        from_csv_youtube_channel['banner_image_url'] = YouTube.from_api_banner(
                            from_api_youtube_channel)
                        from_csv_youtube_channel['videos_count'] = YouTube.from_api_videos_count(
                            from_api_youtube_channel)
                        from_csv_youtube_channel['views_count'] = YouTube.from_api_views_count(
                            from_api_youtube_channel)
                        from_csv_youtube_channel['subscribers_count'] = YouTube.from_api_subscribers_count(
                            from_api_youtube_channel)
                        from_csv_youtube_channel['timestamp'] = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S")
                        break
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

    def __youtube_channel_from_url(self, url) -> dict | None:
        page = self.session.get(url)
        try:
            tree = html.document_fromstring(
                page.content.decode(encoding='iso-8859-1'))
            js_text = tree.xpath(
                '//script[contains(., "ytInitialData")]/text()')[0]
            data = json.loads(
                js_text[js_text.find('{'):js_text.rfind('}') + 1])
            return data['header']['c4TabbedHeaderRenderer']
        except Exception:
            return None

    @staticmethod
    def from_api_fetch_channels_for(channel_ids):
        return youtube_service().channels().list(
            part="snippet,statistics,brandingSettings",
            id=",".join(channel_ids)
        ).execute()

    @staticmethod
    def channel_id_on(youtube_channel) -> str | None:
        if 'channelId' in youtube_channel:
            return youtube_channel['channelId']
        return None

    @staticmethod
    def channel_title_on(youtube_channel) -> str | None:
        if 'title' in youtube_channel:
            return youtube_channel['title']
        return None

    @staticmethod
    def badges_on(youtube_channel) -> str | None:
        if 'badges' not in youtube_channel:
            return None

        def map_badge(badge):
            if 'metadataBadgeRenderer' in badge and \
                    'icon' in badge['metadataBadgeRenderer'] and \
                    'iconType' in badge['metadataBadgeRenderer']['icon']:
                return badge['metadataBadgeRenderer']['icon']['iconType']
            return None
        items = list(filter(lambda x: x is not None, list(
            map(map_badge, youtube_channel['badges']))))
        return '+'.join(items)

    @staticmethod
    def is_membership_active_on(youtube_channel) -> str | None:
        if 'sponsorButton' in youtube_channel:
            return True
        return False

    @staticmethod
    def profile_image_url_on(youtube_channel) -> str | None:
        if 'avatar' in youtube_channel and \
            'thumbnails' in youtube_channel['avatar'] and \
                len(youtube_channel['avatar']['thumbnails']) > 0:
            return youtube_channel['avatar']['thumbnails'][-1]['url'].split('=', 1)[0]
        return None

    @staticmethod
    def banner_image_url_on(youtube_channel) -> str | None:
        if 'banner' in youtube_channel and \
            'thumbnails' in youtube_channel['banner'] and \
                len(youtube_channel['banner']['thumbnails']) > 0:
            return youtube_channel['banner']['thumbnails'][-1]['url'].split('=', 1)[0]
        return None

    @staticmethod
    def links_on(youtube_channel) -> list:
        if 'headerLinks' not in youtube_channel or \
                'channelHeaderLinksRenderer' not in youtube_channel['headerLinks']:
            return []
        header_links_prop = youtube_channel['headerLinks']['channelHeaderLinksRenderer']
        header_links_raw = []
        if 'primaryLinks' in header_links_prop:
            header_links_raw += header_links_prop['primaryLinks']
        if 'secondaryLinks' in header_links_prop:
            header_links_raw += header_links_prop['secondaryLinks']

        def map_header_links(link):
            url = ContentPlatform.parse_redirect_link_from(
                link['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url'])
            platform = ContentPlatform.parse_platform_from(url)
            return {
                'text': link['title']['simpleText'],
                'url': url,
                'platform': platform,
                'username': ContentPlatform.parse_username_from(url, platform)
            }

        def filter_username(link): return link['username'] is not None
        links = list(filter(filter_username, list(
            map(map_header_links, header_links_raw))))
        return links

    @staticmethod
    def from_api_thumbnail(from_api_youtube_channel):
        if 'snippet' in from_api_youtube_channel \
                and 'thumbnails' in from_api_youtube_channel['snippet'] \
                and 'default' in from_api_youtube_channel['snippet']['thumbnails'] \
                and 'url' in from_api_youtube_channel['snippet']['thumbnails']['default']:
            return from_api_youtube_channel['snippet']['thumbnails']['default']['url']
        else:
            return None

    @staticmethod
    def from_api_banner(from_api_youtube_channel):
        if 'brandingSettings' in from_api_youtube_channel \
                and 'image' in from_api_youtube_channel['brandingSettings'] \
                and 'bannerExternalUrl' in from_api_youtube_channel['brandingSettings']['image']:
            return from_api_youtube_channel['brandingSettings']['image']['bannerExternalUrl']
        else:
            return None

    @staticmethod
    def from_api_videos_count(from_api_youtube_channel):
        if 'statistics' in from_api_youtube_channel \
                and 'videoCount' in from_api_youtube_channel['statistics']:
            return from_api_youtube_channel['statistics']['videoCount']
        else:
            return 0

    @staticmethod
    def from_api_views_count(from_api_youtube_channel):
        if 'statistics' in from_api_youtube_channel \
                and 'viewCount' in from_api_youtube_channel['statistics']:
            return from_api_youtube_channel['statistics']['viewCount']
        else:
            return 0

    @staticmethod
    def from_api_subscribers_count(from_api_youtube_channel):
        if 'statistics' in from_api_youtube_channel \
                and 'subscriberCount' in from_api_youtube_channel['statistics']:
            return from_api_youtube_channel['statistics']['subscriberCount']
        else:
            return 0
