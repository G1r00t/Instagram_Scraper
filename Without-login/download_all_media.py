#!/usr/bin/env python3
"""
Download all media from media info JSONs
This script downloads all images/videos from the media info JSON files
"""

import json
import os
import requests
from urllib.parse import urlparse
import time
def fetch_urls(obj):
    """Recursively fetch all URLs, skipping profile_pic_url"""
    urls = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            # Skip keys that contain 'profile_pic'
            if 'profile_pic' in k:
                continue
            # Collect URLs from other keys named 'url'
            if k == 'url' and isinstance(v, str):
                urls.append(v)
            else:
                urls.extend(fetch_urls(v))
    elif isinstance(obj, list):
        for item in obj:
            urls.extend(fetch_urls(item))
    return urls

def download_all_media():
    """Download all images/videos from media info JSONs"""
    
    print(f"📋 Downloading all media from media info JSONs")
    print("=" * 60)
    
    media_info_dir = "media_info"
    save_folder = "instagram_media"
    
    if not os.path.exists(media_info_dir):
        print(f"❌ Error: {media_info_dir} directory not found!")
        return
    
    os.makedirs(save_folder, exist_ok=True)
    
    # Get all JSON files
    json_files = [f for f in os.listdir(media_info_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"❌ No JSON files found in {media_info_dir}")
        return
    
    print(f"📁 Found {len(json_files)} media info JSON files")
    
    all_urls = []
    
    # Extract URLs from all JSON files
    for json_file in json_files:
        file_path = os.path.join(media_info_dir, json_file)
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            urls = fetch_urls(data)
            all_urls.extend(urls)
            print(f"📄 {json_file}: Found {len(urls)} URLs")
            
        except Exception as e:
            print(f"❌ Error reading {json_file}: {e}")
    
    print(f"\n📊 Total URLs found: {len(all_urls)}")
    
    # Keep track of base URLs to avoid duplicates
    seen_bases = set()
    downloaded_urls = []
    
    for url in all_urls:
        if '.jpg' in url:
            base = url.split('.jpg')[0] + '.jpg'
        elif '.mp4' in url:
            base = url.split('.mp4')[0] + '.mp4'
        else:
            continue

        if base not in seen_bases:
            seen_bases.add(base)
            downloaded_urls.append(url)
    
    print(f"📊 {len(downloaded_urls)} unique media to download")
    
    # Download each unique media
    successful_downloads = 0
    failed_downloads = 0
    
    for i, url in enumerate(downloaded_urls, 1):
        ext = url.split('?')[0].split('.')[-1]  # extension
        filename = os.path.join(save_folder, f'media_{i}.{ext}')
        
        print(f"[{i:3d}/{len(downloaded_urls)}] Downloading {url} -> {filename}")
        
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            
            print(f"     ✅ Successfully downloaded")
            successful_downloads += 1
            
        except Exception as e:
            print(f"     ❌ Failed to download: {e}")
            failed_downloads += 1
        
        # Add delay between downloads
        if i < len(downloaded_urls):
            time.sleep(0.5)
    
    print(f"\n📊 Media Download Summary:")
    print(f"✅ Successful downloads: {successful_downloads}")
    print(f"❌ Failed downloads: {failed_downloads}")
    print(f"📁 Files saved to: {save_folder}/")

if __name__ == "__main__":
    print("🚀 Downloading all media from media info JSONs")
    print("=" * 60)
    download_all_media()
