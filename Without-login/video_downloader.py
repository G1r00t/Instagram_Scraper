#!/usr/bin/env python3
"""
Instagram Video Downloader
Extracts unique .mp4 URLs from multiple_pages_result.json and downloads them
"""

import json
import os
import requests
import time
from urllib.parse import urlparse
from typing import Set, List, Dict, Any

class InstagramVideoDownloader:
    def __init__(self, json_file: str = "multiple_pages_result.json", download_dir: str = "downloaded_videos"):
        self.json_file = json_file
        self.download_dir = download_dir
        self.downloaded_urls: Set[str] = set()
        self.failed_downloads: List[Dict[str, Any]] = []
        
        # Create download directory
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Headers for requests (to mimic browser)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def extract_unique_video_urls(self) -> List[Dict[str, Any]]:
        """
        Extract unique .mp4 URLs from the JSON file
        
        Returns:
            List of unique video info dictionaries
        """
        print(f"🔍 Loading JSON file: {self.json_file}")
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: {self.json_file} not found!")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            return []
        
        print(f"✅ Loaded JSON file successfully")
        
        unique_videos = []
        seen_urls: Set[str] = set()
        
        # Process each page
        for page_num, page_data in enumerate(data, 1):
            if not page_data.get('success', False):
                continue
                
            posts = page_data.get('posts', [])
            print(f"📄 Processing page {page_num}: {len(posts)} posts")
            
            # Process each post
            for post in posts:
                subtype = post.get('subtype_name_for_REST__', 'unknown')
                has_video_versions = 'video_versions' in post
                
                # Check if this is a video post (XDTClipsMedia) and has video_versions
                if (subtype != 'XDTClipsMedia' or not has_video_versions):
                    continue
                
                video_versions = post['video_versions']
                post_id = post.get('pk', 'unknown')
                post_code = post.get('code', 'unknown')
                
                # Process each video version
                for version in video_versions:
                    url = version.get('url', '')
                    
                    if not url or '.mp4' not in url:
                        continue
                    
                    # Extract base URL without query parameters to identify unique videos
                    base_url = url.split('?')[0]
                    
                    if base_url not in seen_urls:
                        seen_urls.add(base_url)
                        
                        video_info = {
                            'url': url,
                            'base_url': base_url,
                            'post_id': post_id,
                            'post_code': post_code,
                            'height': version.get('height', 0),
                            'width': version.get('width', 0),
                            'bandwidth': version.get('bandwidth', 0),
                            'type': version.get('type', 0),
                            'id': version.get('id', ''),
                            'filename': f"{post_id}_{post_code}.mp4"
                        }
                        
                        unique_videos.append(video_info)
        
        print(f"🎯 Found {len(unique_videos)} unique videos")
        return unique_videos

    def download_video(self, video_info: Dict[str, Any]) -> bool:
        """
        Download a single video
        
        Args:
            video_info: Dictionary containing video information
            
        Returns:
            bool: True if download successful, False otherwise
        """
        url = video_info['url']
        filename = video_info['filename']
        filepath = os.path.join(self.download_dir, filename)
        
        # Skip if file already exists
        if os.path.exists(filepath):
            print(f"⏭️  Skipping {filename} (already exists)")
            return True
        
        print(f"📥 Downloading: {filename}")
        print(f"   URL: {url[:100]}...")
        print(f"   Size: {video_info['width']}x{video_info['height']}")
        
        try:
            response = requests.get(url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size if available
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Show progress for large files
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r   Progress: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='', flush=True)
            
            if total_size > 0:
                print()  # New line after progress
            
            # Verify file was created and has content
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                file_size = os.path.getsize(filepath)
                print(f"✅ Downloaded: {filename} ({file_size:,} bytes)")
                return True
            else:
                print(f"❌ Download failed: {filename} (empty file)")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Download failed: {filename} - {e}")
            self.failed_downloads.append({
                'video_info': video_info,
                'error': str(e)
            })
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {filename} - {e}")
            self.failed_downloads.append({
                'video_info': video_info,
                'error': str(e)
            })
            return False

    def download_all_videos(self, max_videos: int = None, delay: float = 1.0) -> Dict[str, Any]:
        """
        Download all unique videos
        
        Args:
            max_videos: Maximum number of videos to download (None for all)
            delay: Delay between downloads in seconds
            
        Returns:
            Dictionary with download statistics
        """
        print("🚀 Starting video download process")
        print("=" * 60)
        
        # Extract unique video URLs
        unique_videos = self.extract_unique_video_urls()
        
        if not unique_videos:
            print("❌ No videos found to download")
            return {'success': False, 'error': 'No videos found'}
        
        # Limit number of videos if specified
        if max_videos and max_videos < len(unique_videos):
            unique_videos = unique_videos[:max_videos]
            print(f"📊 Limiting to {max_videos} videos")
        
        print(f"📊 Total videos to download: {len(unique_videos)}")
        print(f"📁 Download directory: {self.download_dir}")
        print(f"⏱️  Delay between downloads: {delay}s")
        print()
        
        successful_downloads = 0
        skipped_downloads = 0
        
        # Download each video
        for i, video_info in enumerate(unique_videos, 1):
            print(f"[{i:2d}/{len(unique_videos)}] ", end='')
            
            if self.download_video(video_info):
                successful_downloads += 1
            else:
                skipped_downloads += 1
            
            # Add delay between downloads to avoid rate limiting
            if i < len(unique_videos):
                time.sleep(delay)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"✅ Successful downloads: {successful_downloads}")
        print(f"⏭️  Skipped (already exists): {skipped_downloads}")
        print(f"❌ Failed downloads: {len(self.failed_downloads)}")
        print(f"📁 Files saved to: {self.download_dir}/")
        
        if self.failed_downloads:
            print(f"\n❌ Failed downloads:")
            for failure in self.failed_downloads:
                print(f"   - {failure['video_info']['filename']}: {failure['error']}")
        
        return {
            'success': True,
            'total_videos': len(unique_videos),
            'successful_downloads': successful_downloads,
            'skipped_downloads': skipped_downloads,
            'failed_downloads': len(self.failed_downloads),
            'failed_list': self.failed_downloads
        }

    def list_videos(self) -> None:
        """List all unique videos without downloading"""
        print("📋 Listing all unique videos")
        print("=" * 60)
        
        unique_videos = self.extract_unique_video_urls()
        
        if not unique_videos:
            print("❌ No videos found")
            return
        
        print(f"🎯 Found {len(unique_videos)} unique videos:")
        print()
        
        for i, video_info in enumerate(unique_videos, 1):
            print(f"{i:2d}. {video_info['filename']}")
            print(f"    Post ID: {video_info['post_id']}")
            print(f"    Post Code: {video_info['post_code']}")
            print(f"    Resolution: {video_info['width']}x{video_info['height']}")
            print(f"    Bandwidth: {video_info['bandwidth']:,} bps")
            print(f"    Type: {video_info['type']}")
            print(f"    URL: {video_info['url'][:100]}...")
            print()

def main():
    """Main function"""
    print("🎬 Instagram Video Downloader")
    print("=" * 60)
    
    # Initialize downloader
    downloader = InstagramVideoDownloader()
    
    # Ask user what to do
    print("Choose an option:")
    print("1. List all videos (no download)")
    print("2. Download all videos")
    print("3. Download first 5 videos (test)")
    print("4. Download first 10 videos")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            downloader.list_videos()
        elif choice == "2":
            result = downloader.download_all_videos()
        elif choice == "3":
            result = downloader.download_all_videos(max_videos=5)
        elif choice == "4":
            result = downloader.download_all_videos(max_videos=10)
        else:
            print("❌ Invalid choice")
            return
        
        if choice in ["2", "3", "4"]:
            if result['success']:
                print(f"\n🎉 Download completed!")
            else:
                print(f"\n❌ Download failed: {result.get('error', 'Unknown error')}")
                
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Download interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
