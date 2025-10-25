# Instagram Scraping Without Login - Technical Writeup


## Problem 
- Instagram only displays the first 12 posts of any public profile to non-authenticated users
- Need to access additional posts beyond the initial 12
- Download all media content (videos, images, carousel posts) from profiles

## Solution Architecture

### Phase 1: Pagination Solution
**Challenge**: Instagram uses `max_id` parameter for pagination in their REST API
**Solution**: Implemented pagination using Instagram's REST API endpoint `/api/v1/feed/user/{user_id}/`

<!-- **Key Files**:
- `working_pagination.py` - Main pagination implementation
- `instagram_pagination_solver.py` - Comprehensive pagination solution with both GraphQL and REST API approaches -->

**Technical Details**:
- Uses REST API endpoint: `https://www.instagram.com/api/v1/feed/user/{user_id}/`
- Pagination parameter: `max_id` (not `end_cursor` as used in GraphQL)
- Authentication: Uses basic headers without session tokens
- Result: Successfully fetches 20+ pages of posts (191 total posts)

### Phase 2: Media Extraction and Download

#### 2.1 Video Downloads (No Login Required)
**Implementation**: Direct download from video URLs found in pagination results
**File**: `video_downloader.py`
- Extracts `.mp4` URLs from `multiple_pages_result.json`
- Handles URL deduplication (same video with different quality parameters)
- Downloads unique videos using `curl` commands
- **Result**: Successfully downloaded all unique videos

#### 2.2 Carousel Images (Requires Session)
**Challenge**: Carousel images require individual media info requests
**Solution**: Extract media IDs and download media info JSONs

**Key Files**:
- `extract_media_ids.py` - Extracts 191 unique media IDs from pagination results
- `download_media_info.py` - Downloads media info JSONs for each media ID
- `download_all_media.py` - Downloads all images/videos from media info JSONs
- `complete_media_downloader.py` - End-to-end solution combining all steps

**Technical Details**:
- Media IDs extracted from `pk` field in pagination results
- Uses authenticated curl commands with session tokens
- Downloads individual media info JSONs containing image URLs
- Recursively extracts all media URLs from JSON structures
- Handles deduplication and downloads unique media files

## Code Files Overview

### Core Pagination Files
1. **`working_pagination.py`** - Main working pagination implementation
   - Uses REST API with `max_id` parameter
   - Fetches 20 pages of posts
   - Saves results to `multiple_pages_result.json`

2. **`instagram_pagination_solver.py`** - Comprehensive pagination solution
   - Implements both GraphQL and REST API approaches
   - Fallback mechanisms for different API endpoints
   - Error handling and retry logic

### Media Extraction Files
3. **`extract_media_ids.py`** - Media ID extraction
   - Parses `multiple_pages_result.json`
   - Extracts unique media IDs from `pk` fields
   - Saves to `extracted_media_ids.txt`

4. **`video_downloader.py`** - Video downloader
   - Extracts `.mp4` URLs from pagination results
   - Handles URL deduplication
   - Downloads videos using curl commands

### Media Info Download Files
5. **`download_media_info.py`** - Media info downloader
   - Downloads individual media info JSONs
   - Uses authenticated curl commands
   - Requires session tokens for carousel images

6. **`download_all_media.py`** - Complete media downloader
   - Downloads all images/videos from media info JSONs
   - Recursive URL extraction from JSON structures
   - Handles deduplication and file naming

### Comprehensive Solution
7. **`complete_media_downloader.py`** - End-to-end solution
   - Combines all steps into single workflow
   - Extracts media IDs → Downloads media info → Downloads all media
   - Complete automation of the entire process

### Authentication Files
8. **`d.py`** - Media info downloader with authentication
   - Updated with working authentication tokens
   - Uses curl commands with proper headers
   - Handles individual media info requests

## Technical Implementation Details

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
multiple_pages_result.json → extract_media_ids.py → extracted_media_ids.txt
                                                           ↓
media_info JSONs ← download_media_info.py ← extracted_media_ids.txt
       ↓
instagram_media/ ← download_all_media.py ← media_info JSONs
```

So complete workflow looks like this

```bash
# Step 1: Extract tokens and user ID
python3 browser.py

# Step 2: Fetch multiple pages of posts  
python3 working_pagination.py

# Step 3: Download videos (no auth required)
python3 video_downloader.py

# Step 4: Extract media IDs
python3 extract_media_ids.py

# Step 5: Download media info (requires auth)
python3 download_media_info.py

# Step 6: Download all media files
python3 download_all_media.py
```

## Results Achieved
- **Total Posts Fetched**: 191 posts across 16 pages
- **Videos Downloaded**: all unique videos (no login required)
- **Media Info Files**: all media info JSONs downloaded successfully
- **Authentication**: Working session-based authentication for carousel images

## Limitations and Considerations
1. **Rate Limiting**: Implemented delays between requests to avoid rate limiting
2. **Session Expiry**: Authentication tokens may expire and need refresh
3. **Carousel Images**: Require authenticated requests (session tokens)
4. **Videos**: Can be downloaded without authentication
5. **API Changes**: Instagram may change API endpoints or parameters

## Future Enhancements
1. **Automated Token Refresh**: Implement automatic token refresh mechanism
2. **Batch Processing**: Optimize for large-scale downloads
3. **Error Recovery**: Enhanced error handling and retry mechanisms
4. **Metadata Extraction**: Extract additional metadata from media info JSONs
5. **Progress Tracking**: Better progress tracking for large downloads

## Conclusion
The solution successfully demonstrates how to:
- Bypass Instagram's 12-post limitation using pagination
- Download videos without authentication
- Access carousel images with proper authentication
- Implement a complete end-to-end scraping workflow

This approach provides a robust foundation for Instagram content extraction while respecting platform limitations and implementing proper authentication where required.
