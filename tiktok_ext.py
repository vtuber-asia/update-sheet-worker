import requests
from lxml import html
import json


def fetch_tiktok_channel(username, retries_left=5):
    url = f"https://www.tiktok.com/{username}"
    try:
        if retries_left == 0:
            return None
        page = requests.get(url, allow_redirects=False)
        print(f'Got page for {username}: {page.status_code}, retries left: {retries_left}')
        if page.status_code != 200:
            raise UnsuccessfulResponse
        tree = html.document_fromstring(page.content.decode(encoding='iso-8859-1'))
        paths = tree.xpath('//script[@id="SIGI_STATE"]')
        data = json.loads(paths[0].text)
        unique_id = data['UserPage']['uniqueId']
        tiktok_user = {
            'username': username,
            'id': data['UserModule']['users'][unique_id]['id'],
            'thumbnail': data['UserModule']['users'][unique_id]['avatarThumb'],
            'followers_count': data['UserModule']['stats'][unique_id]['followerCount'],
            'hearts_count': data['UserModule']['stats'][unique_id]['heartCount'],
            'videos_count': data['UserModule']['stats'][unique_id]['videoCount'],
        }
        return tiktok_user
    except UnsuccessfulResponse:
        return None
    except Exception as e:
        return fetch_tiktok_channel(username, retries_left - 1)


def fetch_tiktok_channels(usernames, pool):
    tiktok_users = pool.map(fetch_tiktok_channel, usernames)
    return list(filter(lambda x: x is not None, tiktok_users))


class UnsuccessfulResponse(Exception):
    pass


if __name__ == '__main__':
    print(fetch_tiktok_channel('@oll13k'))
