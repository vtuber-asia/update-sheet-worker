from upload import Upload
from csv import DictReader
from youtube import YouTube
from content_platform import ContentPlatform


class UploadYouTube(Upload):

    def cell_ranges(self) -> list:
        return [
            'YouTube!A3:P',
        ]

    def data_from(self) -> list:
        usernames = YouTube(self.session, self.logger).fetch_username_cells()
        with open(self.csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv_youtube_channels = list(DictReader(csvfile))
            csvfile.close()
        cells = []
        for username in usernames:
            if username is not None:
                rows = list(filter(lambda row: row['username'].lower() == ContentPlatform.remove_handler_from(
                    username).lower(), from_csv_youtube_channels))
                if len(rows) > 0:
                    cells.append(UploadYouTube.map_to_cell_from(rows[0]))
                else:
                    cells.append(['', '', '', '', '', '', '', '', '', '', ''])
            else:
                cells.append(['', '', '', '', '', '', '', '', '', '', ''])
        return [
            {
                'range': 'Summary!H3:R',
                'values': cells,
            },
            {
                'range': self.cell_ranges()[0],
                'values': list(map(UploadYouTube.map_to_cell_with_xlookup_from, from_csv_youtube_channels))
            }
        ]

    @staticmethod
    def map_to_cell_from(row) -> list:
        return [
            UploadYouTube.cell_username_from(row),
            UploadYouTube.cell_channel_id_from(row),
            UploadYouTube.cell_channel_title_from(row),
            UploadYouTube.cell_badge_from(row),
            UploadYouTube.cell_is_membership_active_from(row),
            UploadYouTube.cell_profile_image_url_from(row),
            UploadYouTube.cell_banner_image_url_from(row),
            UploadYouTube.cell_subscribers_count_from(row),
            UploadYouTube.cell_videos_count_from(row),
            UploadYouTube.cell_views_count_from(row),
            UploadYouTube.cell_timestamp_from(row),
        ]

    @staticmethod
    def map_to_cell_with_xlookup_from(row) -> list:
        return [
            UploadYouTube.cell_username_from(row),
            UploadYouTube.cell_channel_id_from(row),
            UploadYouTube.cell_channel_title_from(row),
            UploadYouTube.cell_badge_from(row),
            UploadYouTube.cell_is_membership_active_from(row),
            UploadYouTube.cell_profile_image_url_from(row),
            UploadYouTube.cell_banner_image_url_from(row),
            UploadYouTube.cell_subscribers_count_from(row),
            UploadYouTube.cell_videos_count_from(row),
            UploadYouTube.cell_views_count_from(row),
            f'=XLOOKUP("@{row["username"]}";Summary!$H$3:$H;Summary!$B$3:$B)',
            f'=XLOOKUP("@{row["username"]}";Summary!$H$3:$H;Summary!$C$3:$C)',
            f'=XLOOKUP("@{row["username"]}";Summary!$H$3:$H;Summary!$E$3:$E)',
            f'=XLOOKUP("@{row["username"]}";Summary!$H$3:$H;Summary!$F$3:$F)',
            f'=XLOOKUP("@{row["username"]}";Summary!$H$3:$H;Summary!$D$3:$D)',
            UploadYouTube.cell_timestamp_from(row),
        ]

    @staticmethod
    def cell_username_from(row):
        if 'username' in row:
            return f'=hyperlink("https://youtube.com/@{row["username"].lower()}"; "@{row["username"].lower()}")'
        return ''

    @staticmethod
    def cell_channel_id_from(row):
        if 'channel_id' in row:
            return row['channel_id']
        return ''

    @staticmethod
    def cell_channel_title_from(row):
        if 'channel_title' in row and row['channel_title'] and 'username' in row and row['username']:
            return f'=hyperlink("https://youtube.com/@{row["username"].lower()}"; "{row["channel_title"]}")'
        return ''

    @staticmethod
    def cell_badge_from(row):
        if 'badges' in row:
            if row['badges'] == 'CHECK_CIRCLE_THICK':
                return '✅'
            if row['badges'] == 'OFFICIAL_ARTIST_BADGE':
                return '🎵'
        return '⬜'

    @staticmethod
    def cell_is_membership_active_from(row):
        if 'is_membership_active' in row and row['is_membership_active'].lower() == 'true':
            return '⭐️'
        return '🔅'

    @staticmethod
    def cell_profile_image_url_from(row):
        if 'profile_image_url' in row:
            return f'=image("{row["profile_image_url"]}"; 4; 80; 80)'
        return ''

    @staticmethod
    def cell_banner_image_url_from(row):
        if 'banner_image_url' in row:
            return f'=image("{row["banner_image_url"]}"; 4; 73; 130)'
        return ''

    @staticmethod
    def cell_videos_count_from(row):
        if 'videos_count' in row:
            return row['videos_count']
        return ''

    @staticmethod
    def cell_views_count_from(row):
        if 'views_count' in row:
            return row['views_count']
        return ''

    @staticmethod
    def cell_subscribers_count_from(row):
        if 'subscribers_count' in row:
            return row['subscribers_count']
        return ''

    @staticmethod
    def cell_timestamp_from(row):
        if 'timestamp' in row:
            return row['timestamp']
        return ''
