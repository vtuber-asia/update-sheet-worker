from csv import DictReader
from os import getenv
from content_platform import ContentPlatform
from gservices import gspread_service
from upload import TryingToUploadEmptySheet, Upload
from upload_youtube import UploadYouTube
from youtube_by_channel_ids import YouTubeByChannelIds


class UploadYouTubeByChannelIds(Upload):

    def data_from(self) -> list:
        usernames = YouTubeByChannelIds(
            self.session, self.logger
        ).fetch_username_cells()
        with open(self.csv_filename, "r", newline="", encoding="utf-8") as csvfile:
            from_csv_youtube_channels = list(DictReader(csvfile))
            csvfile.close()
        cells_part_1 = []
        cells_part_2 = []
        for username in usernames:
            if username is not None:
                rows = list(
                    filter(
                        lambda row: row["channel_id"].lower()
                        == ContentPlatform.remove_handler_from(username).lower(),
                        from_csv_youtube_channels,
                    )
                )
                if len(rows) > 0:
                    cells_part_1.append(
                        UploadYouTubeByChannelIds.map_to_cell_from_part_1(rows[0])
                    )
                    cells_part_2.append(
                        UploadYouTubeByChannelIds.map_to_cell_from_part_2(rows[0])
                    )
                else:
                    cells_part_1.append(["", "", ""])
                    cells_part_2.append(["", "", "", "", "", ""])
            else:
                cells_part_1.append(["", "", ""])
                cells_part_2.append(["", "", "", "", "", ""])
        return [
            {
                "range": "DataSource!H3:J",
                "values": cells_part_1,
            },
            {
                "range": self.cell_ranges()[0],
                "values": list(map(UploadYouTubeByChannelIds.map_to_cell_from_part_1, from_csv_youtube_channels)),
            },
            {
                "range": "DataSource!M3:R",
                "values": cells_part_2,
            },
            {
                "range": self.cell_ranges()[1],
                "values": list(map(UploadYouTubeByChannelIds.map_to_cell_from_part_3, from_csv_youtube_channels)),
            },
        ]
    
    def upload(self):
        self.logger.info(f"Uploading {self.csv_filename} to Google Sheet ...")
        data = self.data_from()
        if self.is_empty_data(data):
            raise TryingToUploadEmptySheet(f"Data on {self.csv_filename} is empty, upload canceled.")
        self.clear_data_on_sheet()
        return [
            gspread_service().spreadsheets().values().batchUpdate(
                spreadsheetId=getenv("GOOGLE_SHEET_ID_SRC"),
                body={
                    'valueInputOption': 'USER_ENTERED',
                    'data': [data[0], data[2]],
                },
            ).execute(),
            gspread_service().spreadsheets().values().batchUpdate(
                spreadsheetId=getenv("GOOGLE_SHEET_ID_DEST"),
                body={
                    'valueInputOption': 'USER_ENTERED',
                    'data': [data[1], data[3]],
                },
            ).execute()
        ]
    
    def clear_data_on_sheet(self):
        return gspread_service().spreadsheets().values().batchClear(
            spreadsheetId=getenv("GOOGLE_SHEET_ID_DEST"),
            body={
                'ranges': self.cell_ranges(),
            },
        ).execute()
    
    def cell_ranges(self) -> list:
        return [
            "YouTube!A3:C",
            "YouTube!F3:P"
        ]

    @staticmethod
    def map_to_cell_from_part_1(row) -> list:
        return [
            UploadYouTube.cell_username_from(row),
            UploadYouTube.cell_channel_id_from(row),
            UploadYouTube.cell_channel_title_from(row),
        ]

    @staticmethod
    def map_to_cell_from_part_2(row) -> list:
        return [
            UploadYouTube.cell_profile_image_url_from(row),
            UploadYouTube.cell_banner_image_url_from(row),
            UploadYouTube.cell_subscribers_count_from(row),
            UploadYouTube.cell_videos_count_from(row),
            UploadYouTube.cell_views_count_from(row),
            UploadYouTube.cell_timestamp_from(row),
        ]

    @staticmethod
    def map_to_cell_from_part_3(row) -> list:
        return [
            UploadYouTube.cell_profile_image_url_from(row),
            UploadYouTube.cell_banner_image_url_from(row),
            UploadYouTube.cell_subscribers_count_from(row),
            UploadYouTube.cell_videos_count_from(row),
            UploadYouTube.cell_views_count_from(row),
            f'=XLOOKUP("{row["channel_id"]}";Profile!$F$3:$F;Profile!$B$3:$B)',
            f'=XLOOKUP("{row["channel_id"]}";Profile!$F$3:$F;Profile!$C$3:$C)',
            f'=XLOOKUP("{row["channel_id"]}";Profile!$F$3:$F;Profile!$E$3:$E)',
            f'=XLOOKUP(XLOOKUP("{
                row["channel_id"]
            }";Profile!$F$3:$F;Profile!$E$3:$E);Groups!$C$3:$C;Groups!$B$3:$B)',
            f'=XLOOKUP("{row["channel_id"]}";Profile!$F$3:$F;Profile!$D$3:$D)',
            UploadYouTube.cell_timestamp_from(row),
        ]
