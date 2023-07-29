from gservices import gspread_service
import requests
import os
from datetime import datetime


def fetch_twitter_usernames_cells():
    return gspread_service().spreadsheets().values().get(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="AB3:AB"
    ).execute()


def fetch_twitter_usernames():
    values = fetch_twitter_usernames_cells()["values"]
    return [value[0] for value in values if len(value) > 0]


def find_twitter_user(users, twitter_username):
    for user in users:
        if 'legacy' in user and 'screen_name' in user['legacy'] and user['legacy']['screen_name'] == twitter_username[1:]:
            return user
    return None


def store_twitter_users(users):
    twitter_usernames_cells = fetch_twitter_usernames_cells()["values"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_rows = []
    for twitter_username_rows in twitter_usernames_cells:
        if len(twitter_username_rows) > 0:
            twitter_user = find_twitter_user(users, twitter_username_rows[0])
            if twitter_user is not None:
                write_rows.append([
                    cell_blue_checkmark(twitter_user),
                    cell_profile_image(twitter_user),
                    cell_banner_image(twitter_user),
                    cell_favorite_count(twitter_user),
                    cell_followers_count(twitter_user),
                    cell_following_count(twitter_user),
                    cell_media_count(twitter_user),
                    cell_tweets_count(twitter_user),
                    cell_possible_sensitive(twitter_user),
                    timestamp,
                ])
            else:
                write_rows.append([
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ])
        else:
            write_rows.append([
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ])
    body = {
        "values": write_rows
    }
    return gspread_service().spreadsheets().values().update(
        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
        range="AC3:AL",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


def generate_twitter_guest_token():
    response = requests.post(
        'https://api.twitter.com/1.1/guest/activate.json',
        headers={
            'Authorization': f'Bearer {os.getenv("TWITTER_API_ACCESS_KEY")}',
        }
    )
    return response.json()


def fetch_twitter_user(username, guest_token=None):
    if guest_token is None:
        guest_token = generate_twitter_guest_token()['guest_token']
    print(f'Using guest token {guest_token}, fetching twitter user for {username} ...')
    response = requests.get(
        os.getenv('TWITTER_API_ENDPOINT'), 
        headers={
            'Accept': '*/*',
            'Authorization': f'Bearer {os.getenv("TWITTER_API_ACCESS_KEY")}',
            'X-Client-Transaction-Id': os.getenv('TWITTER_API_TRANSACTION_ID'),
            'X-Guest-Token': guest_token
        },
        params={
            'variables': '{"screen_name":"' + username + '","withSafetyModeUserFields":true}',
            'features': '{"hidden_profile_likes_enabled":false,"hidden_profile_subscriptions_enabled":false,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}',
            'fieldToggles': '{"withAuxiliaryUserLabels":false}'
        }
    )
    json = response.json()
    limit_remaining = response.headers['x-rate-limit-remaining']
    if limit_remaining == '0':
        guest_token = None
    if 'data' in json and 'user' in json['data'] and 'result' in json['data']['user']:
        return json['data']['user']['result'], guest_token
    return None, guest_token


def cell_blue_checkmark(user):
    if user['is_blue_verified']:
        return f'=IMAGE("{os.getenv("TWITTER_BLUE_BADGE_URL")}"; 4; 20; 20)'
    else:
        return ''


def cell_profile_image(user):
    if 'legacy' in user and 'profile_image_url_https' in user['legacy']:
        return f'=IMAGE("{user["legacy"]["profile_image_url_https"]}"; 4; 80; 80)'
    return ''


def cell_banner_image(user):
    if 'legacy' in user and 'profile_banner_url' in user['legacy']:
        return f'=IMAGE("{user["legacy"]["profile_banner_url"]}"; 4; 50; 150)'
    return ''


def cell_favorite_count(user):
    if 'legacy' in user and 'favourites_count' in user['legacy']:
        return user['legacy']['favourites_count']
    return ''


def cell_followers_count(user):
    if 'legacy' in user and 'followers_count' in user['legacy']:
        return user['legacy']['followers_count']
    return ''


def cell_following_count(user):
    if 'legacy' in user and 'friends_count' in user['legacy']:
        return user['legacy']['friends_count']
    return ''


def cell_media_count(user):
    if 'legacy' in user and 'media_count' in user['legacy']:
        return user['legacy']['media_count']
    return ''


def cell_tweets_count(user):
    if 'legacy' in user and 'statuses_count' in user['legacy']:
        return user['legacy']['statuses_count']
    return ''


def cell_possible_sensitive(user):
    if 'legacy' in user and 'possibly_sensitive' in user['legacy'] and user['legacy']['possibly_sensitive'] == True:
        return '🔴'
    return '🟢'    
