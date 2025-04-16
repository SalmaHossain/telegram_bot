#oauth.py
from googleapiclient.http import MediaFileUpload
import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build



CREDENTIALS_DIR = 'credentials'

os.makedirs(CREDENTIALS_DIR, exist_ok=True)



# GOOGLE DRIVE
def generate_google_oauth_url(user_id):
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri='http://localhost:8080/google/callback'
    )
    flow.redirect_uri = 'http://localhost:8080/google/callback'
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        state=str(user_id),
        include_granted_scopes='true'
    )
    return auth_url

def save_user_credentials(user_id, credentials):
    path = os.path.join(CREDENTIALS_DIR, f"{user_id}.json")
    with open(path, 'w') as f:
        json.dump({
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }, f)

def get_user_credentials(user_id):
    path = os.path.join(CREDENTIALS_DIR, f"{user_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
        return Credentials(**data)

def handle_google_callback(code, state):
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri='http://localhost:8080/google/callback'
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials
    user_id = state
    save_user_credentials(user_id, credentials)
    print(f"✅ Google Drive connected for user {user_id}")

def upload_to_google_drive(user_id, file_path):
    creds = get_user_credentials(user_id)
    if not creds:
        raise Exception("User not authenticated.")
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True)

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name'
    ).execute()

    return uploaded_file

def list_drive_files(user_id):
    creds = get_user_credentials(user_id)
    if not creds:
        raise Exception("User not authenticated.")
    service = build('drive', 'v3', credentials=creds)

    results = service.files().list(
        pageSize=10,
        fields="files(id, name)"
    ).execute()

    return results.get('files', [])




