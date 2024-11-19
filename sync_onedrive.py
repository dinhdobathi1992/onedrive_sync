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
    base_folder = os.path.basename(local_folder_path)

    # Walk through the local folder
    for root, dirs, files in os.walk(local_folder_path):
        # Get fresh token for each operation
        access_token = token_manager.get_valid_token()

        # Rest of your upload_folder code...
        rel_path = os.path.relpath(root, UPLOAD_FOLDER)
        if rel_path == '.':
            rel_path = base_folder
        else:
            rel_path = os.path.join(base_folder, rel_path)

        for dir_name in dirs:
            folder_path = os.path.join(rel_path, dir_name)
            print(f"Creating folder: {folder_path}")
            create_folder(folder_path, access_token)

        for file_name in files:
            # Get fresh token before each file upload
            access_token = token_manager.get_valid_token()

            local_file_path = os.path.join(root, file_name)
            onedrive_path = f"{rel_path}/{file_name}"

            # Your existing file upload logic...
            print(f"Uploading: {onedrive_path}")
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

            if response.status_code in [201, 200]:
                print(f"Successfully uploaded: {onedrive_path}")
            else:
                print(f"Failed to upload {onedrive_path}: {response.json()}")

# Sync files
def sync_files():
    token_manager = TokenManager(CLIENT_ID, TENANT_ID, CLIENT_SECRET)
    upload_folder(UPLOAD_FOLDER, token_manager)


if __name__ == "__main__":
    sync_files()
