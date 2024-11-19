# OneDrive Folder Sync Script

A Python script to sync local folders with OneDrive using Microsoft Graph API. This script supports automatic token refresh for long-running operations and maintains folder hierarchy during upload.

## The Problem

It all started with my trusty old Mac Mini from 2018. Like a loyal companion, it had been by my side through countless projects and late-night coding sessions. However, as time passed, it began showing its age, particularly when dealing with modern cloud sync solutions.

The breaking point came when I tried running the official OneDrive client. What should have been a simple background process turned into a daily struggle. My once-reliable Mac Mini would transform into an electronic heater – fan whirring like a small jet engine, the system gasping for breath with every sync operation.

Opening Activity Monitor became a morning ritual, only to find OneDrive hoarding RAM like a digital dragon, leaving mere scraps for other applications. Simple tasks like opening a browser or responding to emails became an exercise in patience. The symptoms were impossible to ignore:

- OneDrive client greedily consuming over 70% of my available RAM
- System response time slowing to a crawl during sync operations
- Random freezes that required force restarts
- Fan noise so loud it became a running joke in video calls
- CPU temperature rising faster than my frustration

## The Search for Solutions

Determined to find a solution, I embarked on what felt like a digital odyssey. First, I tried the obvious route – the official OneDrive client. "Surely, there must be some settings to make it more resource-friendly," I thought. After hours of tweaking and optimization attempts, I had to admit defeat. My aging Mac Mini simply couldn't handle it.

Next, I turned to the OneDrive web interface. While this worked for basic file access, it quickly became apparent that manually uploading large folders and maintaining file structure was about as efficient as trying to empty the ocean with a teaspoon.

The search led me down various rabbit holes:
1. OneDrive CLI tools seemed promising until I discovered they were either Windows-centric or abandoned macOS support years ago
2. Third-party sync tools either wanted a monthly subscription (adding up to more than my OneDrive subscription itself) or had reliability issues that made me question their safety
3. Various hacky solutions from forums that seemed more likely to create problems than solve them

It was clear that if I wanted a solution that worked for my specific needs, I'd have to build it myself. And thus began the journey of creating this Python script – a lightweight, efficient solution that would only run when needed, giving my loyal Mac Mini the respect and rest it deserves.

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
