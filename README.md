# OneDrive Folder Sync Script

A Python script to sync local folders with OneDrive using Microsoft Graph API. This script supports automatic token refresh for long-running operations and maintains folder hierarchy during upload.

## Context

This script was created to address a specific sync issue with an older Mac Mini that struggles to run the official OneDrive client continuously. Instead of running the resource-intensive OneDrive software constantly, this script provides a lightweight alternative for end-of-day (EOD) synchronization.

### Why This Script?

- **Hardware Limitations**: Older Mac Mini experiencing performance issues with continuous OneDrive sync
- **Resource Efficiency**: Eliminates the need for constant background syncing
- **Scheduled Sync**: Designed for EOD (End of Day) sync operations
- **Acceptable Risk**: 24-hour data loss window is acceptable for this use case
- **Token Management**: Implements automatic token refresh for sync operations longer than 1 hour

### Key Benefits

1. **Resource Friendly**: Only runs when needed, not continuously
2. **Long-Running Operations**: Handles extended sync sessions with token refresh
3. **Maintains Structure**: Preserves folder hierarchy during sync
4. **Simple Setup**: Minimal configuration required
5. **Low Overhead**: Doesn't impact system performance during work hours

### Use Case

Perfect for:
- Systems with limited resources
- Environments where real-time sync isn't critical
- EOD backup scenarios
- Large folder structures requiring extended sync time
- Users who prefer scheduled syncs over continuous synchronization

The script is particularly useful when:
- You need to sync large amounts of data
- System resources are limited
- Immediate file sync isn't crucial
- You want to control when synchronization occurs

## Prerequisites

- Python 3.x
- Microsoft Azure Account
- Registered Azure Application with appropriate permissions
- OneDrive for Business account

## Required Python Packages
```
pip install msal requests
```


## Azure Setup

1. Register a new application in Azure Portal (portal.azure.com)
2. Under "API Permissions" add:
   - Files.ReadWrite.All
   - User.Read.All
3. Generate a Client Secret
4. Note down:
   - Client ID
   - Tenant ID
   - Client Secret

## Configuration

Update the following variables in the script:

```
CLIENT_ID = "your-client-id" # Azure App Client ID
TENANT_ID = "your-tenant-id" # Azure Tenant ID
CLIENT_SECRET = "your-client-secret" # Azure App Client Secret
USER_ID = "user@yourdomain.com" # OneDrive user email
UPLOAD_FOLDER = "/path/to/local/folder" # Local folder to upload
ONEDRIVE_UPLOAD_PATH = "destination" # OneDrive destination folder
```


## Features

- Automatic token refresh for long operations
- Maintains folder hierarchy
- Creates folders if they don't exist
- Handles large file uploads
- Error handling and logging

## Usage

1. Configure the script with your credentials and paths
2. Run the script: `python sync_onedrive.py`



## How It Works

1. The script uses the Microsoft Authentication Library (MSAL) for authentication
2. Creates a token manager to handle OAuth token refresh
3. Walks through the local folder structure
4. Creates corresponding folders in OneDrive
5. Uploads files while maintaining the folder structure
6. Provides upload status feedback

## Error Handling

The script includes error handling for:
- Authentication failures
- Token expiration
- File upload errors
- Network issues

## Security Note

Keep your CLIENT_SECRET secure and never commit it to version control. Consider using environment variables or a configuration file for sensitive information.

## Limitations

- Requires appropriate OneDrive for Business permissions
- Token refresh every hour
- File size limitations based on OneDrive quotas

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Your chosen license]
