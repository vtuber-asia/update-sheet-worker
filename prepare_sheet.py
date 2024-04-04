from gservices import gspread_service, gdrive_service
from inquirer import Text, Confirm, prompt


def create_sheet(title):
    spreadsheet = {
        'properties': {
            'title': title
        },
    }
    return gspread_service().spreadsheets().create(
        body=spreadsheet
    ).execute()


def create_permission(file_id, email, role):
    permission = {
        'type': 'user',
        'role': role,
        'emailAddress': email
    }
    return gdrive_service().permissions().create(
        fileId=file_id,
        body=permission,
        fields='id'
    ).execute()


def publish_readonly(file_id):
    permission = {
        'role': 'reader',
        'type': 'anyone'
    }
    return gdrive_service().permissions().create(
        fileId=file_id,
        body=permission,
        fields='id'
    ).execute()


def prevent_share(file_id):
    resource = {
        'writersCanShare': True,
        'copyRequiresWriterPermission': True
    }
    return gdrive_service().files().update(
        fileId=file_id,
        body=resource,
    ).execute()


if __name__ == '__main__':
    questions = [
        Text(
            'sheet_title',
            message='Spreadsheet Title '
        ),
        Text(
            'writer_email',
            message='Writer / Editor Email '
        ),
        Confirm(
            'publish_readonly',
            message='Do you want to publish your spreadsheet?',
            default=True
        ),
        Confirm(
            'prevent_share',
            message='Do you want to prevent your spreadsheet to be shared / downloaded by non-writer?',
            default=True
        )
    ]
    answers = prompt(questions)
    created = create_sheet(answers['sheet_title'])
    spreadsheet_id = created.get('spreadsheetId')
    spreadsheet_url = created.get('spreadsheetUrl')
    create_permission(spreadsheet_id, answers['writer_email'], 'writer')
    if answers['publish_readonly']:
        publish_readonly(spreadsheet_id)
    if answers['prevent_share']:
        prevent_share(spreadsheet_id)
    print(
        f'Spreadsheet has been created, you can access the document here: {
            spreadsheet_url
        }'
    )
