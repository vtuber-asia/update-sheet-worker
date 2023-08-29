import os
from csv import DictReader

from content_platform import ContentPlatform
from twitter import Twitter
from upload import Upload


class UploadTwitter(Upload):

    def cell_ranges(self) -> list:
        return [
            'Twitter!A3:U',
        ]
    
    def data_from(self, csv_filename) -> list:
        username = Twitter(self.session, self.logger).fetch_username_cells()
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv = list(DictReader(csvfile))
            csvfile.close()
        cells = []
        for username in username:
            if username is not None:
                rows = list(filter(lambda row: row['username'].lower() == ContentPlatform.remove_handler_from(
                    username).lower(), from_csv))
                if len(rows) > 0:
                    cells.append(UploadTwitter.map_to_cell_from(rows[0]))
                else:
                    cells.append(['', '', '', '', '', '', '', '', '', '', '', ''])
            else:
                cells.append(['', '', '', '', '', '', '', '', '', '', '', ''])
        return [
            {
                'range': 'Summary!AY3:BJ',
                'values': cells,
            },
            {
                'range': self.cell_ranges()[0],
                'values': list(map(UploadTwitter.map_to_cell_with_xlookup_from, from_csv))
            }
        ]
    
    @staticmethod
    def map_to_cell_from(row) -> list:
        return [
            UploadTwitter.cell_username_from(row),
            UploadTwitter.cell_name_from(row),
            UploadTwitter.cell_is_verified_from(row),
            UploadTwitter.cell_profile_image_url_from(row),
            UploadTwitter.cell_banner_image_url_from(row),
            UploadTwitter.cell_followers_count_from(row),
            UploadTwitter.cell_following_count_from(row),
            UploadTwitter.cell_media_count_from(row),
            UploadTwitter.cell_tweets_count_from(row),
            UploadTwitter.cell_favorites_count_from(row),
            UploadTwitter.cell_possible_sensitive_from(row),
            UploadTwitter.cell_timestamp_from(row),
        ]
    
    @staticmethod
    def map_to_cell_with_xlookup_from(row) -> list:
        return [
            UploadTwitter.cell_username_from(row),
            UploadTwitter.cell_name_from(row),
            UploadTwitter.cell_profile_image_url_from(row),
            UploadTwitter.cell_banner_image_url_from(row),
            UploadTwitter.cell_followers_count_from(row),
            UploadTwitter.cell_following_count_from(row),
            UploadTwitter.cell_media_count_from(row),
            UploadTwitter.cell_tweets_count_from(row),
            UploadTwitter.cell_favorites_count_from(row),
            UploadTwitter.cell_possible_sensitive_from(row),
            f'=XLOOKUP("@{row["username"]}";Summary!$AY$3:$AY;Summary!$B$3:$B)',
            f'=XLOOKUP("@{row["username"]}";Summary!$AY$3:$AY;Summary!$C$3:$C)',
            f'=XLOOKUP("@{row["username"]}";Summary!$AY$3:$AY;Summary!$E$3:$E)',
            f'=XLOOKUP("@{row["username"]}";Summary!$AY$3:$AY;Summary!$F$3:$F)',
            UploadTwitter.cell_is_verified_from(row),
            f'=XLOOKUP("@{row["username"]}";Summary!$AY$3:$AY;Summary!$D$3:$D)',
            UploadTwitter.cell_timestamp_from(row),
        ]
    
    @staticmethod
    def cell_username_from(row):
        if 'username' in row and row['username']:
            return f'=hyperlink("https://twitter.com/{row["username"].lower()}"; "@{row["username"]}")'
        return ''
    
    @staticmethod
    def cell_name_from(row):
        if 'name' in row and row['name'] and 'username' in row and row['username']:
            return f'=hyperlink("https://twitter.com/{row["username"].lower()}"; "{row["name"]}")'
        return ''
    
    @staticmethod
    def cell_is_verified_from(row):
        if 'is_verified' in row and row['is_verified'] and row['is_verified'].lower() == 'true':
            return f'=image("{os.getenv("TWITTER_BLUE_BADGE_URL")}"; 4; 20; 20)'
        return ''
    
    @staticmethod
    def cell_profile_image_url_from(row):
        if 'profile_image_url' in row and row['profile_image_url']:
            return f'=image("{row["profile_image_url"]}")'
        return ''
    
    @staticmethod
    def cell_banner_image_url_from(row):
        if 'banner_image_url' in row and row['banner_image_url']:
            return f'=image("{row["banner_image_url"]}"; 4; 50; 150)'
        return ''
    
    @staticmethod
    def cell_favorites_count_from(row):
        if 'favorites_count' in row and row['favorites_count']:
            return row['favorites_count']
        return ''
    
    @staticmethod
    def cell_followers_count_from(row):
        if 'followers_count' in row and row['followers_count']:
            return row['followers_count']
        return ''
    
    @staticmethod
    def cell_following_count_from(row):
        if 'following_count' in row and row['following_count']:
            return row['following_count']
        return ''
    
    @staticmethod
    def cell_media_count_from(row):
        if 'media_count' in row and row['media_count']:
            return row['media_count']
        return ''
    
    @staticmethod
    def cell_tweets_count_from(row):
        if 'tweets_count' in row and row['tweets_count']:
            return row['tweets_count']
        return ''
    
    @staticmethod
    def cell_possible_sensitive_from(row):
        if 'possible_sensitive' in row and row['possible_sensitive'] and row['possible_sensitive'].lower() == 'true':
            return '✔️'
        return ''
    
    @staticmethod
    def cell_timestamp_from(row):
        if 'timestamp' in row and row['timestamp']:
            return row['timestamp']
        return ''
    
    
