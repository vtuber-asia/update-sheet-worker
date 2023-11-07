from gservices import gdrive_service


def update_writer_permission(file_id):
    resource = {
        'writersCanShare': True,
        'copyRequiresWriterPermission': True
    }
    return gdrive_service().files().update(
        fileId=file_id,
        body=resource,
    ).execute()

if __name__ == '__main__':
    from dotenv import load_dotenv
    import os
    load_dotenv(override=True)
    file_id = os.getenv('GOOGLE_SHEET_ID')
    print(file_id)
    created = update_writer_permission(file_id)
    print(created)
