from upload import Upload
from csv import DictReader
from youtube import YouTube
from content_platform import ContentPlatform


class UploadYouTube(Upload):

    def data_from(self, csv_filename) -> list:
        usernames = YouTube(self.session, self.logger).fetch_username_cells()
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            from_csv_youtube_channels = list(DictReader(csvfile))
            csvfile.close()
        cells = []
        for username in usernames:
            if username is not None:
                rows = list(filter(lambda row: row['username'] == ContentPlatform.remove_handler_from(
                    username), from_csv_youtube_channels))
                if len(rows) > 0:
                    cells.append([
                        UploadYouTube.cell_username_from(rows[0]),
                        UploadYouTube.cell_channel_id_from(rows[0]),
                        UploadYouTube.cell_channel_title_from(rows[0]),
                        UploadYouTube.cell_badge_from(rows[0]),
                        UploadYouTube.cell_is_membership_active_from(rows[0]),
                        UploadYouTube.cell_profile_image_url_from(rows[0]),
                        UploadYouTube.cell_banner_image_url_from(rows[0]),
                        UploadYouTube.cell_videos_count_from(rows[0]),
                        UploadYouTube.cell_views_count_from(rows[0]),
                        UploadYouTube.cell_subscribers_count_from(rows[0]),
                        UploadYouTube.cell_timestamp_from(rows[0]),
                    ])
                else:
                    cells.append(['', '', '', '', '', '', '', '', '', '', ''])
            else:
                cells.append(['', '', '', '', '', '', '', '', '', '', ''])
        return [
            {
                'range': 'Summary!G3:Q',
                'values': cells
            }
        ]

    @staticmethod
    def cell_username_from(row):
        if 'username' in row:
            return f'=hyperlink("https://youtube.com/{row["username"]}"; "@{row["username"]}")'
        return None

    @staticmethod
    def cell_channel_id_from(row):
        if 'channel_id' in row:
            return row['channel_id']
        return None

    @staticmethod
    def cell_channel_title_from(row):
        if 'channel_title' in row:
            return row['channel_title']
        return None

    @staticmethod
    def cell_badge_from(row):
        if 'badges' in row:
            return row['badges']
        return None

    @staticmethod
    def cell_is_membership_active_from(row):
        if 'is_membership_active' in row and row['is_membership_active'] is True:
            return f'=image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Yellow_Star_with_rounded_edges.svg/42px-Yellow_Star_with_rounded_edges.svg.png"; 4; 24; 24)'
        return None

    @staticmethod
    def cell_profile_image_url_from(row):
        if 'profile_image_url' in row:
            return f'=image("{row["profile_image_url"]}"; 4; 80; 80)'
        return None

    @staticmethod
    def cell_banner_image_url_from(row):
        if 'banner_image_url' in row:
            return f'=image("{row["banner_image_url"]}"; 4; 73; 130)'
        return None

    @staticmethod
    def cell_videos_count_from(row):
        if 'videos_count' in row:
            return row['videos_count']
        return None

    @staticmethod
    def cell_views_count_from(row):
        if 'views_count' in row:
            return row['views_count']
        return None

    @staticmethod
    def cell_subscribers_count_from(row):
        if 'subscribers_count' in row:
            return row['subscribers_count']
        return None

    @staticmethod
    def cell_timestamp_from(row):
        if 'timestamp' in row:
            return row['timestamp']
        return None
