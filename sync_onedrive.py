import os
import requests
from msal import ConfidentialClientApplication
import time
from datetime import datetime, timedelta
# Configuration
CLIENT_ID = "xxx"  # Replace with your Azure App Client ID
TENANT_ID = "xxxx"  # Replace with your Azure Tenant ID
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
UPLOAD_FOLDER = "xxxx"  # Local folder to upload
ONEDRIVE_UPLOAD_PATH = "xxx"  # OneDrive destination folder
CLIENT_SECRET = "xxx" # Replace with your Azure Client Secret
USER_ID = "xxxx" # Replace with your account email
IGNORE_FOLDERS = [
    '.terragrunt-cache',
    'node_modules',
    '.git',
    '__pycache__',
    '.terraform'
]
CACHE_FILE = 'sync_cache.json'

def load_cache():
    """Load the sync cache from file"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save the sync cache to file"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_file_hash(file_path):
    """Calculate MD5 hash of file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def should_upload_file(file_path, cache):
    """Check if file should be uploaded based on cache"""
    if file_path not in cache:
        return True

    current_hash = get_file_hash(file_path)
    current_mtime = os.path.getmtime(file_path)

    return (current_hash != cache[file_path]['hash'] or
            current_mtime != cache[file_path]['mtime'])

# Authentication
class TokenManager:
    def __init__(self, client_id, tenant_id, client_secret):
        self.client_id = client_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.client_secret = client_secret
        self.token = None
        self.token_expires_at = None
        self.app = ConfidentialClientApplication(
            client_id,
            authority=self.authority,
            client_credential=client_secret
        )

    def get_valid_token(self):
        # Check if token exists and is still valid (with 5 min buffer)
        if self.token and self.token_expires_at and datetime.now() < (self.token_expires_at - timedelta(minutes=5)):
            return self.token

        # Get new token
        result = self.app.acquire_token_for_client(scopes=SCOPE)

        if "access_token" in result:
            self.token = result['access_token']
            # Set expiration time (usually 1 hour from now)
            self.token_expires_at = datetime.now() + timedelta(seconds=result['expires_in'])
            return self.token
        else:
            print(f"Error: {result.get('error')}")
            print(f"Error description: {result.get('error_description')}")
            raise Exception("Failed to get access token")


# File upload function
def upload_file(file_path, access_token):
    file_name = os.path.basename(file_path)
    upload_url = f"https://graph.microsoft.com/v1.0/users/{USER_ID}/drive/root:/{ONEDRIVE_UPLOAD_PATH}/{file_name}:/content"

    with open(file_path, 'rb') as file:
        response = requests.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/octet-stream"
            },
            data=file
        )
    return response.status_code, response.json()

def upload_large_file(file_path, relative_path, access_token):
    """Handle large file uploads using chunked upload"""
    file_size = os.path.getsize(file_path)

    # Create upload session
    create_session_url = f"https://graph.microsoft.com/v1.0/users/{USER_ID}/drive/root:/{ONEDRIVE_UPLOAD_PATH}/{relative_path}:/createUploadSession"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    session_response = requests.post(create_session_url, headers=headers)
    if session_response.status_code != 200:
        print(f"Failed to create upload session for {relative_path}: {session_response.json()}")
        return False

    upload_url = session_response.json()['uploadUrl']

    # Upload in chunks
    chunk_size = 10 * 1024 * 1024  # 10MB chunks
    with open(file_path, 'rb') as file:
        chunk_number = 0
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break

            start = chunk_number * chunk_size
            end = start + len(chunk) - 1

            headers = {
                'Content-Length': str(len(chunk)),
                'Content-Range': f'bytes {start}-{end}/{file_size}'
            }

            success = False
            retries = 3
            while not success and retries > 0:
                try:
                    response = requests.put(upload_url, headers=headers, data=chunk)
                    if response.status_code in [200, 201, 202]:
                        success = True
                        print(f"Uploaded chunk {chunk_number + 1} of {relative_path}")
                    else:
                        print(f"Failed to upload chunk {chunk_number + 1}. Retrying...")
                        retries -= 1
                except Exception as e:
                    print(f"Error uploading chunk {chunk_number + 1}: {str(e)}")
                    retries -= 1

            if not success:
                return False

            chunk_number += 1

    return True

def create_folder(folder_name, access_token):
    url = f"https://graph.microsoft.com/v1.0/users/{USER_ID}/drive/root:/{ONEDRIVE_UPLOAD_PATH}/{folder_name}:/children"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "name": folder_name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "replace"
    }

    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 201



def upload_folder(local_folder_path, token_manager):
    """Enhanced folder upload with caching and ignore patterns"""
    cache = load_cache()
    new_cache = {}
    base_folder = os.path.basename(local_folder_path)

    for root, dirs, files in os.walk(local_folder_path):
        # Filter out ignored folders
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        access_token = token_manager.get_valid_token()
        rel_path = os.path.relpath(root, UPLOAD_FOLDER)

        if rel_path == '.':
            rel_path = base_folder
        else:
            rel_path = os.path.join(base_folder, rel_path)

        # Create necessary folders
        for dir_name in dirs:
            if not any(ignore in dir_name for ignore in IGNORE_FOLDERS):
                folder_path = os.path.join(rel_path, dir_name)
                print(f"Checking/Creating folder: {folder_path}")
                create_folder(folder_path, access_token)

        # Upload files
        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            onedrive_path = f"{rel_path}/{file_name}"

            if should_upload_file(local_file_path, cache):
                print(f"Uploading changed/new file: {onedrive_path}")
                file_size = os.path.getsize(local_file_path)

                success = False
                if file_size > 4 * 1024 * 1024:  # 4MB threshold
                    success = upload_large_file(local_file_path, onedrive_path, access_token)
                else:
                    # Original small file upload logic
                    upload_url = f"https://graph.microsoft.com/v1.0/users/{USER_ID}/drive/root:/{ONEDRIVE_UPLOAD_PATH}/{onedrive_path}:/content"
                    with open(local_file_path, 'rb') as file:
                        response = requests.put(
                            upload_url,
                            headers={
                                "Authorization": f"Bearer {access_token}",
                                "Content-Type": "application/octet-stream"
                            },
                            data=file
                        )
                        success = response.status_code in [201, 200]

                if success:
                    print(f"Successfully uploaded: {onedrive_path}")
                    # Update cache
                    new_cache[local_file_path] = {
                        'hash': get_file_hash(local_file_path),
                        'mtime': os.path.getmtime(local_file_path)
                    }
                else:
                    print(f"Failed to upload: {onedrive_path}")
            else:
                print(f"Skipping unchanged file: {onedrive_path}")
                new_cache[local_file_path] = cache[local_file_path]

    # Save updated cache
    save_cache(new_cache)

# Sync files
def sync_files():
    token_manager = TokenManager(CLIENT_ID, TENANT_ID, CLIENT_SECRET)
    upload_folder(UPLOAD_FOLDER, token_manager)


if __name__ == "__main__":
    sync_files()

if __name__ == "__main__":
    sync_files()
