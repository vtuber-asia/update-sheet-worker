import requests
from lxml import html
import json
from urllib.parse import urlparse, parse_qs
from tldextract import extract
import os.path


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


def fetch_channel_depths(channel_ids):
    channel_depths = []
    for channel_id in channel_ids:
        channel_depth = fetch_channel_depth(channel_id)
        channel_depths.append(channel_depth)
    return channel_depths


def parse_redirect_link(link):
    parsed_redirect_links = parse_qs(urlparse(link).query)
    if 'q' in parsed_redirect_links and len(parsed_redirect_links['q']) > 0:
        return parsed_redirect_links['q'][0]
    return link


def parse_platform(link):
    return extract(parse_redirect_link(link)).domain


def parse_username(link):
    parsed_redirect_link = parse_redirect_link(link)
    if parsed_redirect_link[:1] == '/':
        parsed_redirect_link = parsed_redirect_link[1:]
    path = urlparse(parsed_redirect_link).path
    split = os.path.split(path)
    def map_split(s): return s.replace('/', '')
    def filter_blank(s): return s != ''
    segments = list(map(map_split, split))
    filtered_segments = list(filter(filter_blank, segments))
    if len(filtered_segments) > 0:
        return filtered_segments[-1]
    return None
