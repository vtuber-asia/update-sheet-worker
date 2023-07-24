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
