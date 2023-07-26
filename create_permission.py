from gservices import gdrive_service


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


def list_permissions(file_id):
    return gdrive_service().permissions().list(
        fileId=file_id,
        fields='*'
    ).execute()


if __name__ == '__main__':
    from dotenv import load_dotenv
    import os
    load_dotenv()
    file_id = os.getenv('GOOGLE_SHEET_ID')
    email = os.getenv('GOOGLE_USER_EMAIL')
    role = 'writer'
    created = create_permission(file_id, email, role)
    readonly = publish_readonly(file_id)
    print("OK")
