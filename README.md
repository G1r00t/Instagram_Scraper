# Instagram Scraper Without Login
## This is for the directory [Without-login](./Without-login) 
### Files present in root requires login so that is a solution with lesser capabilities
A comprehensive solution for scraping Instagram profiles without requiring user authentication. This project demonstrates how to bypass Instagram's 12-post limitation and download all media content from public profiles.

## ⚠️ Disclaimer

This project is for **educational purposes only**. Scraping Instagram may violate their Terms of Service. Use responsibly and ethically. The authors are not responsible for any misuse of this code.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip
- curl (for downloading media)

### Installation
```bash
git clone https://github.com/G1r00t/Instagram_Scraper.git
cd instagram_scraper/Without-login
pip install -r requirements.txt
patchright install #to install the browser for browser automation
```

## 📋 Complete Workflow

### Step 1: Extract Authentication Tokens (Login-based)
```bash
python3 browser_automation.py
```
**Purpose**: Login to Instagram and extract authentication tokens
**Requirements**: `login.txt` with username and password
**Output**: 
- `instagram_data_output/cookies.json` - Authentication cookies
- `instagram_data_output/user_ids.txt` - User IDs
- `instagram_data_output/headers.json` - Browser headers

### Step 2: Fetch Multiple Pages of Posts
```bash
python3 working_pagination.py
```
**Purpose**: Use REST API to fetch multiple pages of posts beyond the initial 12
**Output**: `multiple_pages_result.json` - Complete pagination data

### Step 3: Download Videos (No Authentication Required)
```bash
python3 video_downloader.py
```
**Purpose**: Download all videos from the pagination results
**Output**: `videos/` directory with all downloaded videos

### Step 4: Extract Media IDs
```bash
python3 extract_media_ids.py
```
**Purpose**: Extract unique media IDs from pagination results
**Output**: `extracted_media_ids.txt` - List of all media IDs

### Step 5: Download Media Info (Requires Authentication)
```bash
python3 download_media_info.py
```
**Purpose**: Download detailed media information for each media ID
**Output**: `media_info/` directory with JSON files for each media

### Step 6: Download All Media Files
```bash
python3 download_all_media.py
```
**Purpose**: Download all images and videos from media info JSONs
**Output**: `instagram_media/` directory with all media files

### Alternative: Complete End-to-End Solution
```bash
python3 complete_media_downloader.py
```
**Purpose**: Combines steps 4-6 into a single automated workflow
**Output**: All media files downloaded automatically

## 📁 File Structure

```
instagram-scraper-without-login/
├── browser_automation.py            # Step 1: Login-based token extraction
├── working_pagination.py           # Step 2: Pagination solution
├── video_downloader.py             # Step 3: Video downloads
├── extract_media_ids.py            # Step 4: Media ID extraction
├── download_media_info.py          # Step 5: Media info download
├── download_all_media.py           # Step 6: Complete media download
├── complete_media_downloader.py    # Alternative: End-to-end solution
├── instagram_pagination_solver.py  # Advanced pagination with fallbacks
├── profiles.txt                    # Target Instagram usernames
├── login.txt                       # Instagram login credentials
├── writeup.md                      # Technical documentation
├── requirements.txt                # Python dependencies
├── run_workflow.sh                 # Automated workflow script
└── instagram_data_output/          # Generated data
    ├── cookies.json
    ├── headers.json
    ├── user_ids.txt
    └── network_requests.json
```

## 🔧 Configuration

### login.txt
Add Instagram login credentials:
```
your_username
your_password
```

### profiles.txt
Add Instagram usernames (one per line):
```
instagram
natgeo
nasa
```

### Browser Configuration
Edit `browser.py` to customize:
```python
config = {
    'request_delay': 3,     # Seconds between profile visits
    'headless': False,      # Set to True to hide browser
    'max_retries': 3,       # Max retry attempts
    'timeout': 30000,       # Page timeout in ms
}
```

## 📊 Results

- **Total Posts Fetched**: 191 posts across 20 pages
- **Videos Downloaded**: All unique videos (no login required)
- **Media Info Files**: All media info JSONs downloaded successfully
- **Authentication**: Working session-based authentication for carousel images

## 🛠️ Technical Details

### Authentication Requirements
- **Videos/Reels**: No authentication required
- **Carousel Images**: Requires session tokens and cookies
- **Authentication Tokens Used**:
  - `csrftoken`
  - `sessionid` 
  - `ds_user_id` 
  - `x-web-session-id` 

### API Endpoints Used
1. **Pagination**: `/api/v1/feed/user/{user_id}/`
2. **Media Info**: `/api/v1/media/{media_id}/info/`
3. **Web Profile**: `/api/v1/users/web_profile_info/?username={username}`

### Data Flow
```
browser_automation.py → cookies.json + user_ids.txt
     ↓
working_pagination.py → multiple_pages_result.json
     ↓
video_downloader.py → videos/
     ↓
extract_media_ids.py → extracted_media_ids.txt
     ↓
download_media_info.py → media_info/
     ↓
download_all_media.py → instagram_media/
```

## 🔍 Troubleshooting

### Common Issues
1. **Rate Limiting**: Increase delays between requests
2. **Session Expiry**: Re-run `browser.py` to refresh tokens
3. **Missing Dependencies**: Install requirements.txt
4. **Permission Errors**: Ensure write permissions for output directories

### Error Handling
- All scripts include comprehensive error handling
- Failed downloads are logged and can be retried
- Network timeouts are handled gracefully

## 📈 Performance Tips

1. **Batch Processing**: Process multiple profiles in sequence
2. **Rate Limiting**: Respect Instagram's rate limits
3. **Storage**: Ensure sufficient disk space for media downloads
4. **Network**: Use stable internet connection for large downloads

## 🔒 Security Considerations

- Never commit authentication tokens to version control
- Use environment variables for sensitive data
- Implement proper error handling to avoid exposing tokens
- Respect Instagram's robots.txt and rate limits


---

**Remember**: This tool is for educational purposes only. Always respect Instagram's Terms of Service and use responsibly.
