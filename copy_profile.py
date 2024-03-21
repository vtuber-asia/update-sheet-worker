from os import getenv
from copy_cells import fetch_cells_from, write_cells_to, clear_cells_on


if __name__ == '__main__':
    dest_spreadsheet_id = getenv('GOOGLE_SHEET_ID_DEST')
    source_spreadsheet_id = getenv('GOOGLE_SHEET_ID_SRC')
    print(
        clear_cells_on(
            spreadsheet_id=dest_spreadsheet_id, 
            ranges="Profile!A:K"
        )
    )
    print(write_cells_to(
            dest_spreadsheet_id,
            "Profile!A:E",
            "USER_ENTERED",
            fetch_cells_from(
                source_spreadsheet_id,
                "DataSource!A:E",
                "FORMULA",
            )
        )
    )
    print(write_cells_to(
            dest_spreadsheet_id,
            "Profile!F:F",
            "RAW",
            fetch_cells_from(
                source_spreadsheet_id,
                "DataSource!G:G",
                "FORMULA",
            )
        )
    )
    print(write_cells_to(
            dest_spreadsheet_id,
            "Profile!G:G",
            "RAW",
            fetch_cells_from(
                source_spreadsheet_id,
                "DataSource!T:T",
                "FORMULA",
            )
        )
    )
    print(write_cells_to(
            dest_spreadsheet_id,
            "Profile!H:H",
            "RAW",
            fetch_cells_from(
                source_spreadsheet_id,
                "DataSource!AB:AB",
                "FORMULA",
            )
        )
    )
    print(write_cells_to(
            dest_spreadsheet_id,
            "Profile!I:I",
            "RAW",
            fetch_cells_from(
                source_spreadsheet_id,
                "DataSource!AN:AN",
                "FORMULA",
            )
        )
    )
    print(write_cells_to(
            dest_spreadsheet_id,
            "Profile!J:J",
            "RAW",
            fetch_cells_from(
                source_spreadsheet_id,
                "DataSource!AX:AX",
                "FORMULA",
            )
        )
    )
    print(write_cells_to(
            dest_spreadsheet_id,
            "Profile!K:K",
            "RAW",
            fetch_cells_from(
                source_spreadsheet_id,
                "DataSource!BL:BL",
                "FORMULA",
            )
        )
    )
