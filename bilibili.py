from csv import DictReader, DictWriter
from datetime import datetime

from lxml import html
from requests.exceptions import ChunkedEncodingError

from content_platform import ContentPlatform
from utils import value_to_float


class Bilibili(ContentPlatform):

    def fetch_user(self, username: str) -> dict | None:
        username = ContentPlatform.remove_handler_from(username)
        url = f'https://www.bilibili.tv/en/space/{username}'
        self.logger.info(f"Fetching Bilibili channel info for @{username}")
        try:
            page = self.session.get(url, allow_redirects=False, timeout=10)
            if page.status_code != 200:
                return None
            tree = html.document_fromstring(page.content.decode(encoding='iso-8859-1'))
            bilibili_user = {
                'user_id': username,
                'channel_title': Bilibili.parse_channel_title_from(tree),
                'is_verified': Bilibili.parse_is_verified_from(tree),
                'profile_image_url': Bilibili.parse_profile_image_url_from(tree),
                'followers_count': Bilibili.parse_followers_count_from(tree),
                'following_count': Bilibili.parse_following_count_from(tree),
                'likes_count': Bilibili.parse_likes_count_from(tree),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            if bilibili_user['channel_title'] is None:
                return None
            return bilibili_user
        except ChunkedEncodingError:
            return False
        except Exception as e:
            self.logger.error(f"Error fetching Bilibili channel info for @{username}: {e}")
            return None
    
    def create_csv(self) -> str:
        csv_filename = f'./outputs/{datetime.now().strftime("%Y%m%d%H%M%S")}_bilibili.csv'
        fields = [
            'user_id',
            'channel_title',
            'is_verified',
            'profile_image_url',
            'followers_count',
            'following_count',
            'likes_count',
            'timestamp',
        ]
        with open(csv_filename, 'w', newline='', encoding='iso-8859-1') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields)
            w.writeheader()
            for username in self.fetch_usernames():
                user = False
                while user is False:
                    user = self.fetch_user(username)
                if user is not None:
                    w.writerow(user)
            csvfile.close()
        with open(csv_filename, 'r', newline='', encoding='iso-8859-1') as csvfile:
            from_csv_bilibili_channels = list(DictReader(csvfile))
            csvfile.close()
        with open(csv_filename, 'w', newline='', encoding='iso-8859-1') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            w.writerows(
                sorted(list(
                    filter(lambda row: row is not None,
                           from_csv_bilibili_channels
                    )
                ), key=lambda row: int(row['followers_count']), reverse=True)
            )
            csvfile.close()
        return csv_filename
    
    @staticmethod
    def parse_channel_title_from(tree):
        element = tree.xpath('/html/body/div[1]/div[1]/div/section/main/div/div/div/div[1]/div[2]/h1/text()')
        if len(element) > 0:
            return element[0]
        return None

    @staticmethod
    def parse_is_verified_from(tree):
        return len(tree.xpath('/html/body/div[1]/div[1]/div/section/main/div/div/div/div[1]/div[2]/h1/img')) > 0
    
    @staticmethod
    def parse_profile_image_url_from(tree):
        element = tree.xpath('/html/body/div[1]/div[1]/div/section/main/div/div/div/div[1]/div[1]/picture/source')
        if len(element) > 0 and 'srcset' in element[0].attrib:
            return element[0].attrib['srcset']
        return None
    
    @staticmethod
    def parse_followers_count_from(tree):
        element = tree.xpath('/html/body/div[1]/div[1]/div/section/main/div/div/div/div[1]/div[2]/div/p[2]/a')
        if len(element) > 0:
            return int(value_to_float(element[0].text))
        return 0

    @staticmethod
    def parse_following_count_from(tree):
        element = tree.xpath('/html/body/div[1]/div[1]/div/section/main/div/div/div/div[1]/div[2]/div/p[1]/a')
        if len(element) > 0:
            return int(value_to_float(element[0].text))
        return 0
    
    @staticmethod
    def parse_likes_count_from(tree):
        element = tree.xpath('/html/body/div[1]/div[1]/div/section/main/div/div/div/div[1]/div[2]/div/p[3]/span[1]')
        if len(element) > 0:
            return int(value_to_float(element[0].text))
        return 0
    