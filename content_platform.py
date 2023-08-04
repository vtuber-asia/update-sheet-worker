import os
from logging import Logger
from urllib.parse import parse_qs, urlparse

from requests import Session
from tldextract import extract


class ContentPlatform:

    def __init__(self, session: Session, logger: Logger):
        self.session = session
        self.logger = logger

    def fetch_user(self, username: str) -> dict | None:
        pass

    def fetch_username_cells(self) -> list:
        pass

    def fetch_usernames(self) -> list:
        return list(
            filter(lambda username: username is not None,
                   self.fetch_username_cells())
        )

    def create_csv(self) -> str:
        pass

    @staticmethod
    def parse_platform_from(url) -> str:
        domain = extract(url).domain
        if domain == 'youtube':
            return 'YouTube'
        if domain == 'twitch':
            return 'Twitch'
        if domain == 'facebook':
            return 'Facebook'
        if domain == 'instagram':
            return 'Instagram'
        if domain == 'twitter':
            return 'Twitter'
        if domain == 'tiktok':
            return 'TikTok'
        if domain == 'sociabuzz':
            return 'Sociabuzz'
        if domain == 'bilibili':
            return 'Bstation'
        return domain

    @staticmethod
    def parse_redirect_link_from(url) -> str:
        parsed_redirect_links = parse_qs(urlparse(url).query)
        if 'q' in parsed_redirect_links and len(parsed_redirect_links['q']) > 0:
            return parsed_redirect_links['q'][0]
        return url

    @staticmethod
    def parse_username_from(url, platform=None) -> str | None:
        filtered_segments = list(
            filter(lambda s: s != '' and s != extract(url).fqdn,
                   list(map(lambda s: s.replace('/', ''),
                            os.path.split(
                       urlparse(url).path
                   )
                ))
            )
        )
        if len(filtered_segments) > 0:
            if platform == 'Bstation':
                return filtered_segments[-1]
            return ContentPlatform.remove_handler_from(filtered_segments[0])
        return None

    @staticmethod
    def remove_handler_from(username):
        if username.startswith('@'):
            return username[1:]
        else:
            return username

    @staticmethod
    def cells_on(row):
        return row[0] if len(row) > 0 else None
