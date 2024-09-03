import json
from csv import DictReader, DictWriter
from datetime import datetime
import logging
from time import sleep

from lxml import html

from content_platform import ContentPlatform
from gservices import youtube_service
from setup import setup
from utils import split


class YouTube(ContentPlatform):

    def fetch_user(self, username: str) -> dict | None:
        username = ContentPlatform.remove_handler_from(username)
        url = f'https://www.youtube.com/channel/{username}/about'
        self.logger.info(f'Fetching YouTube channel info for {username} ...')
        youtube_channel, data = self.__youtube_channel_from_url(url)
        if youtube_channel is None:
            self.logger.warning(f'Could not find YouTube channel: @{username}')
            return None
        links = YouTube.links_on(data)
        twitch_links = list(
            filter(lambda link: link['platform'] == 'Twitch', links))
        tiktok_links = list(
            filter(lambda link: link['platform'] == 'TikTok', links))
        twitter_links = list(
            filter(lambda link: link['platform'] == 'Twitter', links))
        bstation_links = list(
            filter(lambda link: link['platform'] == 'Bstation', links))
        instagram_links = list(
            filter(lambda link: link['platform'] == 'Instagram', links))
        return {
            'username': username,
            'channel_id': YouTube.channel_id_on(youtube_channel),
            'channel_title': YouTube.channel_title_on(youtube_channel),
            'badges': YouTube.badges_on(data),
            'is_membership_active': YouTube.is_membership_active_on(data),
            'profile_image_url': YouTube.profile_image_url_on(youtube_channel),
            'banner_image_url': YouTube.banner_image_url_on(youtube_channel),
            'videos_count': 0,
            'views_count': 0,
            'subscribers_count': 0,
            'username_twitch': twitch_links[0]['username'] if len(twitch_links) > 0 else None,
            'username_tiktok': tiktok_links[0]['username'] if len(tiktok_links) > 0 else None,
            'username_twitter': twitter_links[0]['username'] if len(twitter_links) > 0 else None,
            'username_bstation': bstation_links[0]['username'] if len(bstation_links) > 0 else None,
            'username_instagram': instagram_links[0]['username'] if len(instagram_links) > 0 else None,
        }

    def create_csv(self) -> str:
        csv_filename = f'./outputs/{
            datetime.now().strftime("%Y%m%d%H%M%S")
        }_youtube.csv'
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
            'username_instagram',
            'timestamp'
        ]
        with open(csv_filename, 'w', newline='', encoding='iso-8859-1') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            for username in self.fetch_usernames():
                youtube_channel = self.fetch_user(username)
                if youtube_channel is not None:
                    w.writerow(youtube_channel)
                sleep(1)
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

    def __youtube_channel_from_url(self, url) -> (dict | None, dict | None):
        try:
            header, data = self.__tabs_data_from(url)
            return header, data
        except Exception as e:
            self.logger.error(e)
            return None, None

    def __tabs_data_from(self, url, retry: int = 5) -> dict | None:
        try:
            page = self.session.get(
                url,
                timeout=10,
                cookies={
                    'SOCS': 'CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg'
                }
            )
            tree = html.document_fromstring(
                page.content.decode(encoding='iso-8859-1'))
            js_text = tree.xpath(
                '//script[contains(., "ytInitialData")]/text()')[0]
            data = json.loads(
                js_text[js_text.find('{'):js_text.rfind('}') + 1])
            return data['metadata']['channelMetadataRenderer'], data
        except Exception as e:
            self.logger.error(e)
            if isinstance(e, KeyError) and len(e.args) == 1 and e.args[0] == 'channelMetadataRenderer' and retry > 0:
                sleep(5)
                retry_left = retry - 1
                self.session, self.logger = setup(f"id.bungamungil.vtuber-asia-v3.main._{retry_left}-retry-left", logging.DEBUG)
                return self.__tabs_data_from(url, retry_left)
            return None, None

    @staticmethod
    def filter_tab(tab, name):
        if 'tabRenderer' not in tab:
            return False
        return tab['tabRenderer']['endpoint']['commandMetadata']['webCommandMetadata']['url'][(len(name) * -1):] == name

    @staticmethod
    def from_api_fetch_channels_for(channel_ids):
        return youtube_service().channels().list(
            part="snippet,statistics,brandingSettings",
            id=",".join(channel_ids)
        ).execute()

    @staticmethod
    def channel_id_on(youtube_channel) -> str | None:
        if 'externalId' in youtube_channel:
            return youtube_channel['externalId']
        return None

    @staticmethod
    def channel_title_on(youtube_channel) -> str | None:
        if 'title' in youtube_channel:
            return youtube_channel['title']
        return None

    @staticmethod
    def badges_on(data) -> str | None:
        if 'header' not in data:
            return None
        if 'pageHeaderRenderer' not in data['header']:
            return None
        if 'content' not in data['header']['pageHeaderRenderer']: 
            return None
        if 'pageHeaderViewModel' not in data['header']['pageHeaderRenderer']['content']:
            return None
        if 'title' not in data['header']['pageHeaderRenderer']['content']['pageHeaderViewModel']:
            return None
        if 'dynamicTextViewModel' not in data['header']['pageHeaderRenderer']['content']['pageHeaderViewModel']['title']:
            return None
        if 'text' not in data['header']['pageHeaderRenderer']['content']['pageHeaderViewModel']['title']['dynamicTextViewModel']:
            return None
        if 'attachmentRuns' not in data['header']['pageHeaderRenderer']['content']['pageHeaderViewModel']['title']['dynamicTextViewModel']['text']:
            return None
        attachmentRuns = data['header']['pageHeaderRenderer']['content']['pageHeaderViewModel']['title']['dynamicTextViewModel']['text']['attachmentRuns']
        if len(attachmentRuns) == 0:
            return None
        if 'element' not in attachmentRuns[0]:
            return None
        if 'type' not in attachmentRuns[0]['element']:
            return None
        if 'imageType' not in attachmentRuns[0]['element']['type']:
            return None
        if 'image' not in attachmentRuns[0]['element']['type']['imageType']:
            return None
        if 'sources' not in attachmentRuns[0]['element']['type']['imageType']['image']:
            return None
        sources = attachmentRuns[0]['element']['type']['imageType']['image']['sources']
        if len(sources) == 0:
            return None
        if 'clientResource' not in sources[0]:
            return None
        if 'imageName' not in sources[0]['clientResource']:
            return None
        imageName = sources[0]['clientResource']['imageName']
        if imageName == 'MUSIC_FILLED':
            return 'OFFICIAL_ARTIST_BADGE'
        if imageName == 'CHECK_CIRCLE_FILLED':
            return 'CHECK_CIRCLE_THICK'
        return None

    @staticmethod
    def is_membership_active_on(data) -> str | None:
        if len(data['header']['pageHeaderRenderer']['content']['pageHeaderViewModel']['actions']['flexibleActionsViewModel']['actionsRows'][0]['actions']) > 1:
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
    def links_on(data) -> list:
        try:
            header_links_raw = data['onResponseReceivedEndpoints'][0]['showEngagementPanelEndpoint']['engagementPanel'][
                'engagementPanelSectionListRenderer']['content']['sectionListRenderer']['contents'][0][
                'itemSectionRenderer']['contents'][0]['aboutChannelRenderer']['metadata']['aboutChannelViewModel'][
                'links']

            def map_header_links(link):
                url = ContentPlatform.parse_redirect_link_from(
                    link['channelExternalLinkViewModel']['link']['content'])
                platform = ContentPlatform.parse_platform_from(url)
                return {
                    'text': link['channelExternalLinkViewModel']['title']['content'],
                    'url': url,
                    'platform': platform,
                    'username': ContentPlatform.parse_username_from(url, platform)
                }

            def filter_username(link):
                return link['username'] is not None

            links = list(filter(filter_username, list(
                map(map_header_links, header_links_raw))))
            return links
        except KeyError:
            return []

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
