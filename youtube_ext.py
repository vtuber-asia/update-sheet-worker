from lxml import html
from urllib.parse import urlparse, parse_qs
from tldextract import extract
from links import remove_handler
import logging
import os.path
import json
import requests


def fetch_channel_depth(channel_id):
    url = f"https://www.youtube.com/channel/{channel_id}/about"
    page = requests.get(url)
    print(f"Fetching channel depths for {channel_id} ...")
    try:
        tree = html.document_fromstring(
            page.content.decode(encoding='iso-8859-1'))
        js_text = tree.xpath(
            '//script[contains(., "ytInitialData")]/text()')[0]
        data = json.loads(js_text[js_text.find('{'):js_text.rfind('}') + 1])
        header_links_prop = data['header']['c4TabbedHeaderRenderer']['headerLinks']['channelHeaderLinksRenderer']
        header_links_raw = []
        if 'primaryLinks' in header_links_prop:
            header_links_raw += header_links_prop['primaryLinks']
        if 'secondaryLinks' in header_links_prop:
            header_links_raw += header_links_prop['secondaryLinks']
        def map_header_links(link): return {
            'title': link['title']['simpleText'],
            'url': parse_redirect_link(link['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']),
            'platform': parse_platform(link['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']),
            'username': parse_username(link['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url'])
        }
        def filter_username(link): return link['username'] is not None
        links = list(filter(filter_username, list(map(map_header_links, header_links_raw))))
        channel_depth = {
            'youtube_channel_id': channel_id,
            'links': links
        }
        return channel_depth
    except Exception as e:
        print(e)
        return {
            'youtube_channel_id': channel_id,
            'links': []
        }


def youtube_channel_for(username):
    logging.info(f"Writing YouTube channel: {username}")
    youtube_channel = youtube_channel_from_url(f"https://www.youtube.com/{username}")
    if youtube_channel is None:
        logging.warning(f"Could not find YouTube channel: {username}")
        return None
    links = links_on(youtube_channel)
    twitch_links = list(filter(lambda link: link['platform'] == 'Twitch', links))
    tiktok_links = list(filter(lambda link: link['platform'] == 'TikTok', links))
    twitter_links = list(filter(lambda link: link['platform'] == 'Twitter', links))
    return {
        'username': username,
        'channel_id': channel_id_on(youtube_channel),
        'channel_title': channel_title_on(youtube_channel),
        'badges': badges_on(youtube_channel),
        'is_membership_active': is_membership_active_on(youtube_channel),
        'profile_image_url': profile_image_url_on(youtube_channel),
        'banner_image_url': banner_image_url_on(youtube_channel),
        'links': links,
        'username_twitch': twitch_links[0]['username'] if len(twitch_links) > 0 else None,
        'username_tiktok': tiktok_links[0]['username'] if len(tiktok_links) > 0 else None,
        'username_twitter': twitter_links[0]['username'] if len(twitter_links) > 0 else None,
    }


def youtube_channel_from_url(url):
    page = requests.get(url)
    try:
        tree = html.document_fromstring(page.content.decode(encoding='iso-8859-1'))
        js_text = tree.xpath('//script[contains(., "ytInitialData")]/text()')[0]
        data = json.loads(js_text[js_text.find('{'):js_text.rfind('}') + 1])
        return data['header']['c4TabbedHeaderRenderer']
    except Exception:
        return None


def fetch_channel_depths(channel_ids, pool):
    channel_depths = pool.map(fetch_channel_depth, channel_ids)
    return channel_depths


def parse_redirect_link(link):
    parsed_redirect_links = parse_qs(urlparse(link).query)
    if 'q' in parsed_redirect_links and len(parsed_redirect_links['q']) > 0:
        return parsed_redirect_links['q'][0]
    return link


def parse_platform(link):
    domain = extract(parse_redirect_link(link)).domain
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
    return domain


def parse_username(link):
    parsed_redirect_link = parse_redirect_link(link)
    filtered_segments = list(
        filter(lambda s: s != '' and s != extract(parsed_redirect_link).fqdn,
            list(map(lambda s: s.replace('/', ''), 
                os.path.split(
                    urlparse(parsed_redirect_link).path
                )
            ))
        )
    )
    if len(filtered_segments) > 0:
        return remove_handler(filtered_segments[0])
    return None


def channel_id_on(youtube_channel):
    if 'channelId' in youtube_channel:
        return youtube_channel['channelId']
    return None


def channel_title_on(youtube_channel):
    if 'title' in youtube_channel:
        return youtube_channel['title']
    return None


def badges_on(youtube_channel):
    if 'badges' not in youtube_channel:
        return None
    def map_badge(badge):
        if 'metadataBadgeRenderer' in badge and \
                'icon' in badge['metadataBadgeRenderer'] and \
                'iconType' in badge['metadataBadgeRenderer']['icon']:
            return badge['metadataBadgeRenderer']['icon']['iconType']
        return None
    items = list(filter(lambda x: x is not None, list(map(map_badge, youtube_channel['badges']))))
    return '+'.join(items)


def is_membership_active_on(youtube_channel):
    if 'sponsorButton' in youtube_channel:
        return True
    return False


def profile_image_url_on(youtube_channel):
    if 'avatar' in youtube_channel and \
        'thumbnails' in youtube_channel['avatar'] and \
            len(youtube_channel['avatar']['thumbnails']) > 0:
        return youtube_channel['avatar']['thumbnails'][-1]['url'].split('=', 1)[0]
    return None


def banner_image_url_on(youtube_channel):
    if 'banner' in youtube_channel and \
        'thumbnails' in youtube_channel['banner'] and \
            len(youtube_channel['banner']['thumbnails']) > 0:
        return youtube_channel['banner']['thumbnails'][-1]['url'].split('=', 1)[0]
    return None


def links_on(youtube_channel):
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
        url = parse_redirect_link(link['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url'])
        platform = parse_platform(url)
        return {
            'text': link['title']['simpleText'],
            'url': url,
            'platform': platform,
            'username': parse_username(url)
        }
    def filter_username(link): return link['username'] is not None
    links = list(filter(filter_username, list(map(map_header_links, header_links_raw))))
    return links
