import requests
from lxml import html
import json
from links import remove_handler


def fetch_tiktok_channel(username):
    url = f"https://www.tiktok.com/{username}"
    page = requests.get(url)
    print(f"Fetching tiktok user page for {username} ...")
    try:
        tree = html.document_fromstring(
            page.content.decode(encoding='iso-8859-1'))
        js_text = tree.xpath(
            '//script[@id="SIGI_STATE"]')[0]
        data = json.loads(js_text.text)
        username_no_handler = remove_handler(username)
        tiktok_user = {
            'username': username,
            'id': data['UserModule']['users'][username_no_handler]['id'],
            'thumbnail': data['UserModule']['users'][username_no_handler]['avatarThumb'],
            'followers_count': data['UserModule']['stats'][username_no_handler]['followerCount'],
            'hearts_count': data['UserModule']['stats'][username_no_handler]['heartCount'],
            'videos_count': data['UserModule']['stats'][username_no_handler]['videoCount'],
        }
        return tiktok_user
    except Exception as e:
        print(e)
        return None


def fetch_tiktok_channels(usernames):
    tiktok_users = []
    for username in usernames:
        tiktok_user = fetch_tiktok_channel(username)
        if tiktok_user is not None:
            tiktok_users.append(tiktok_user)
    return tiktok_users


if __name__ == '__main__':
    print(fetch_tiktok_channel('@oll13k'))
