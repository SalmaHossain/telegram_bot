from googleapiclient.http import MediaFileUpload
import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import io
from pdfminer.high_level import extract_text as extract_pdf_text
from googleapiclient.http import MediaIoBaseDownload



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





def search_drive_for_text(user_id, query):
    creds = get_user_credentials(user_id)
    if not creds:
        raise Exception("User not authenticated.")
    service = build('drive', 'v3', credentials=creds)

    # Search for text/pdf/docx files (you can change the mimeTypes)
    results = service.files().list(
        q="mimeType='text/plain'",  # Can also try mimeType contains 'text'
        fields="files(id, name)",
        pageSize=20
    ).execute()

    files = results.get('files', [])
    for file in files:
        file_id = file['id']
        file_name = file['name']
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        content = fh.getvalue().decode('utf-8', errors='ignore')
        if query.lower() in content.lower():
            # Return the matching line or the whole content
            for line in content.splitlines():
                if query.lower() in line.lower():
                    return f"📄 *{file_name}*:\n`{line}`"
            return f"📄 *{file_name}* contains relevant information."
    return "🔍 No matching information found."



def search_drive_files(user_id, query):
    creds = get_user_credentials(user_id)
    if not creds:
        raise Exception("User not authenticated.")
    service = build('drive', 'v3', credentials=creds)

    # Fetch list of files in Google Drive
    files = list_drive_files(user_id)
    for file in files:
        if file['name'].endswith('.pdf'):  # Check if the file is a PDF
            file_id = file['id']

            # Download the file
            request = service.files().get_media(fileId=file_id)
            file_path = f"{file['name']}"
            with open(file_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

            # Extract text from the downloaded PDF file
            try:
                text = extract_pdf_text(file_path)
                # Locate the query and extract relevant text
                if query.lower() in text.lower():
                    # Extract lines around the query
                    lines = text.split('\n')
                    response_lines = []
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            # Capture a few lines before and after the match
                            start = max(i - 2, 0)
                            end = min(i + 3, len(lines))
                            response_lines = lines[start:end]
                            break
                    # Format the response
                    response = "\n".join(response_lines)
                    return f"Found in file '{file['name']}':\n\n{response}"
            except Exception as e:
                return f"❌ Error processing file '{file['name']}': {e}"

    return f"'{query}' not found in any PDF files."
