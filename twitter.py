from os import getenv
from datetime import datetime
from logging import Logger

from requests import Session

from content_platform import ContentPlatform
from csv import DictWriter, DictReader


class Twitter(ContentPlatform):

    def __init__(self, session: Session, logger: Logger):
        super().__init__(session, logger)
        self.guest_token = None

    def fetch_user(self, username: str) -> dict | None:
        username = ContentPlatform.remove_handler_from(username)
        self.logger.info(f"Fetching Twitter user info for @{username}")
        if self.guest_token is None:
            self.guest_token = self.generate_twitter_guest_token()[
                'guest_token']
        self.logger.info(
            f'Using guest token {self.guest_token}, fetching twitter user for {username} ...')
        response = self.session.get(
            getenv('TWITTER_API_ENDPOINT'),
            headers={
                'Accept': '*/*',
                'Authorization': f'Bearer {getenv("TWITTER_API_ACCESS_KEY")}',
                'X-Client-Transaction-Id': getenv('TWITTER_API_TRANSACTION_ID'),
                'X-Guest-Token': self.guest_token
            },
            params={
                'variables': '{"screen_name":"' + username + '","withSafetyModeUserFields":true}',
                'features': '{"hidden_profile_likes_enabled":false,"hidden_profile_subscriptions_enabled":false,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}',
                'fieldToggles': '{"withAuxiliaryUserLabels":false}'
            },
            timeout=10,
        )
        json = response.json()
        limit_remaining = response.headers['x-rate-limit-remaining']
        if limit_remaining == '0':
            self.guest_token = None
        if 'data' in json and 'user' in json['data'] and 'result' in json['data']['user']:
            json_data = json['data']['user']['result']
            if 'reason' in json_data:
                self.logger.info(f'Twitter account for @{username} is {json_data["reason"]}')
                return None
            return {
                'username': username,
                'user_id': Twitter.user_id_from(json_data),
                'name': Twitter.name_from(json_data),
                'is_verified': Twitter.has_blue_checkmark_from(json_data),
                'profile_image_url': Twitter.profile_image_from(json_data),
                'banner_image_url': Twitter.banner_image_from(json_data),
                'favorites_count': Twitter.favorites_count_from(json_data),
                'followers_count': Twitter.followers_count_from(json_data),
                'following_count': Twitter.following_count_from(json_data),
                'media_count': Twitter.media_count_from(json_data),
                'tweets_count': Twitter.tweets_count_from(json_data),
                'possible_sensitive': Twitter.possible_sensitive_from(json_data),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        return None

    def create_csv(self) -> str:
        csv_filename = f'./outputs/{datetime.now().strftime("%Y%m%d%H%M%S")}_twitter.csv'
        fields = [
            'username',
            'user_id',
            'name',
            'is_verified',
            'profile_image_url',
            'banner_image_url',
            'favorites_count',
            'followers_count',
            'following_count',
            'media_count',
            'tweets_count',
            'possible_sensitive',
            'timestamp',
        ]
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            for username in self.fetch_usernames():
                user = self.fetch_user(username)
                if user is not None:
                    w.writerow(user)
            csvfile.close()
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv = list(DictReader(csvfile))
            csvfile.close()
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            w = DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            w.writerows(
                sorted(list(
                    filter(lambda row: row is not None,
                           from_csv
                           ),
                ), key=lambda row: int(row['followers_count']), reverse=True)
            )
            csvfile.close()
        return csv_filename

    def generate_twitter_guest_token(self):
        response = self.session.post(
            'https://api.twitter.com/1.1/guest/activate.json',
            headers={
                'Authorization': f'Bearer {getenv("TWITTER_API_ACCESS_KEY")}',
            },
            timeout=10,
        )
        return response.json()
    
    @staticmethod
    def user_id_from(user):
        if 'rest_id' in user:
            return user['rest_id']
        return None

    @staticmethod
    def name_from(user):
        if 'legacy' in user and 'name' in user['legacy']:
            return user['legacy']['name']
        return None

    @staticmethod
    def has_blue_checkmark_from(user):
        if user['is_blue_verified']:
            return True
        else:
            return False

    @staticmethod
    def profile_image_from(user):
        if 'legacy' in user and 'profile_image_url_https' in user['legacy']:
            return user["legacy"]["profile_image_url_https"]
        return None

    @staticmethod
    def banner_image_from(user):
        if 'legacy' in user and 'profile_banner_url' in user['legacy']:
            return user["legacy"]["profile_banner_url"]
        return None

    @staticmethod
    def favorites_count_from(user):
        if 'legacy' in user and 'favourites_count' in user['legacy']:
            return user['legacy']['favourites_count']
        return 0

    @staticmethod
    def followers_count_from(user):
        if 'legacy' in user and 'followers_count' in user['legacy']:
            return user['legacy']['followers_count']
        return 0

    @staticmethod
    def following_count_from(user):
        if 'legacy' in user and 'friends_count' in user['legacy']:
            return user['legacy']['friends_count']
        return 0

    @staticmethod
    def media_count_from(user):
        if 'legacy' in user and 'media_count' in user['legacy']:
            return user['legacy']['media_count']
        return 0

    @staticmethod
    def tweets_count_from(user):
        if 'legacy' in user and 'statuses_count' in user['legacy']:
            return user['legacy']['statuses_count']
        return 0

    @staticmethod
    def possible_sensitive_from(user):
        if 'legacy' in user and 'possibly_sensitive' in user['legacy'] and user['legacy']['possibly_sensitive'] == True:
            return True
        return False
