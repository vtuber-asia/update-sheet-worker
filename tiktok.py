import json
from csv import DictReader, DictWriter
from datetime import datetime
from lxml import html
from content_platform import ContentPlatform


class TikTok(ContentPlatform):

    def fetch_user(self, username: str) -> dict:
        username = ContentPlatform.remove_handler_from(username)
        url = f'https://www.tiktok.com/@{username}'
        self.logger.info(f"Fetching TikTok channel info for @{username}")
        try:
            page = self.session.get(url, allow_redirects=False, timeout=10)
            if page.status_code != 200:
                return None
            tree = html.document_fromstring(
                page.content.decode(encoding='iso-8859-1')
            )
            paths = tree.xpath(
                '//script[@id="__UNIVERSAL_DATA_FOR_REHYDRATION__"]'
            )
            data = json.loads(paths[0].text)
            userInfo = data['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']
            tiktok_user = {
                'username': username,
                'user_id': userInfo['user']['id'],
                'channel_title': userInfo['user']['nickname'],
                'is_verified': userInfo['user']['verified'],
                'profile_image_url': userInfo['user']['avatarLarger'],
                'followers_count': userInfo['stats']['followerCount'],
                'following_count': userInfo['stats']['followingCount'],
                'hearts_count': userInfo['stats']['heartCount'],
                'videos_count': userInfo['stats']['videoCount'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return tiktok_user
        except KeyError:
            self.logger.error(
                f"Couldn't find TikTok channel info for @{username}"
            )
            return None
        except Exception as e:
            self.logger.error(
                f"Error fetching TikTok channel info for @{username}, code : {e}"
            )
            return None

    def create_csv(self) -> str:
        csv_filename = f'./outputs/{datetime.now().strftime("%Y%m%d%H%M%S")}_tiktok.csv'
        fields = [
            'username',
            'user_id',
            'channel_title',
            'is_verified',
            'profile_image_url',
            'followers_count',
            'following_count',
            'hearts_count',
            'videos_count',
            'timestamp',
        ]
        with open(csv_filename, 'w', newline='', encoding='iso-8859-1') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            for username in self.fetch_usernames():
                tiktok_user = False
                while tiktok_user is False:
                    tiktok_user = self.fetch_user(username)
                if tiktok_user is not None:
                    w.writerow(tiktok_user)
            csvfile.close()
        with open(csv_filename, 'r', newline='', encoding='iso-8859-1') as csvfile:
            from_csv_tiktok_users = list(DictReader(csvfile))
            csvfile.close()
        with open(csv_filename, 'w', newline='', encoding='iso-8859-1') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            w.writerows(
                sorted(list(
                    filter(lambda row: row is not None,
                           from_csv_tiktok_users
                           )
                ), key=lambda row: int(row['followers_count']), reverse=True)
            )
            csvfile.close()
        return csv_filename
