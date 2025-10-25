#!/usr/bin/env python3
"""
Complete Instagram Media Downloader
This script:
1. Extracts media IDs from multiple_pages_result.json
2. Downloads media info JSONs for each ID
3. Downloads all images/videos from the media info JSONs
"""

import json
import os
import subprocess
import time
import requests
from urllib.parse import urlparse

def extract_media_ids():
    """Extract all unique media IDs from multiple_pages_result.json"""
    
    json_file = 'multiple_pages_result.json'
    if not os.path.exists(json_file):
        print(f"❌ Error: {json_file} not found!")
        return []
    
    print(f"📋 Loading {json_file}...")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    media_ids = set()
    
    # Extract media IDs from posts - the data is a list of pages
    if isinstance(data, list):
        for page in data:
            if 'posts' in page:
                for post in page['posts']:
                    if 'pk' in post:  # pk is the media ID
                        media_ids.add(post['pk'])
    elif isinstance(data, dict) and 'posts' in data:
        # Handle case where data is a single object with posts
        for post in data['posts']:
            if 'pk' in post:
                media_ids.add(post['pk'])
    
    # Convert set to list and sort
    media_ids_list = sorted(list(media_ids))
    
    print(f"📊 Found {len(media_ids_list)} unique media IDs")
    
    # Save to file
    output_file = 'extracted_media_ids.txt'
    with open(output_file, 'w') as f:
        for media_id in media_ids_list:
            f.write(f"{media_id}\n")
    
    print(f"💾 Media IDs saved to: {output_file}")
    return media_ids_list

def download_media_info(media_ids):
    """Download media info JSON files for all media IDs"""
    
    print(f"\n📋 Downloading media info for {len(media_ids)} media IDs")
    print("=" * 60)
    
    # Create directory for media info files
    media_info_dir = "media_info"
    os.makedirs(media_info_dir, exist_ok=True)
    
    # Updated authentication tokens (you can update these)
    cookies = 'csrftoken=Pm1YaYGv9ztke-ulp2SXzy; datr=8mH8aCFhXPfJ3eVSs_A8V7EX; ig_did=7C47DB9F-834F-4FD9-B441-F90695CC8404; wd=1920x1080; mid=aPxh8gAEAAHCMivwWXjF8lsmHObR; sessionid=77402749614%3AHMwq2YJ1dBgjLX%3A23%3AAYhc34ZIYgsEd290BjEMWV258tKyCHF4xl1T1o7Qqw; ds_user_id=77402749614'
    csrf_token = 'Pm1YaYGv9ztke-ulp2SXzy'
    app_id = '936619743392459'
    web_session_id = 'tx5z52:swmjrc:zunpy8'

    successful_downloads = 0
    failed_downloads = 0
    
    # Download media info for each ID
    for i, media_id in enumerate(media_ids, 1):
        print(f"[{i:3d}/{len(media_ids)}] Downloading media info for ID: {media_id}")
        
        output_file = os.path.join(media_info_dir, f"media_{media_id}.json")
        
        # Skip if file already exists and has content
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"     ⏭️  File already exists, skipping...")
            successful_downloads += 1
            continue
        
        # Construct curl command for this media ID
        curl_cmd = [
            'curl',
            f'https://www.instagram.com/api/v1/media/{media_id}/info/',
            '-H', f'Cookie: {cookies}',
            '-H', f'X-Csrftoken: {csrf_token}',
            '-H', f'X-Ig-App-Id: {app_id}',
            '-H', 'X-Requested-With: XMLHttpRequest',
            '-H', 'Accept: */*',
            '-H', 'Accept-Encoding: gzip, deflate, br, zstd',
            '-H', 'Accept-Language: en-GB,en;q=0.9',
            '-H', 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            '-H', 'Referer: https://www.instagram.com/ohneis652/',
            '-H', f'X-Web-Session-Id: {web_session_id}',
            '-H', 'X-Asbd-Id: 359341',
            '-H', 'X-Ig-Www-Claim: 0',
            '-H', 'Sec-Ch-Prefers-Color-Scheme: dark',
            '-H', 'Sec-Ch-Ua: "Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            '-H', 'Sec-Ch-Ua-Mobile: ?0',
            '-H', 'Sec-Ch-Ua-Platform: "Linux"',
            '-H', 'Sec-Ch-Ua-Platform-Version: "6.5.0"',
            '-H', 'Sec-Fetch-Dest: empty',
            '-H', 'Sec-Fetch-Mode: cors',
            '-H', 'Sec-Fetch-Site: same-origin',
            '--compressed',
            '--silent',
            '--show-error',
            '-o', output_file
        ]
        
        try:
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    try:
                        with open(output_file, 'r') as f:
                            json.load(f)
                        print(f"     ✅ Successfully downloaded")
                        successful_downloads += 1
                    except json.JSONDecodeError:
                        print(f"     ⚠️  Downloaded but invalid JSON")
                        failed_downloads += 1
                else:
                    print(f"     ❌ Failed to download (empty file)")
                    failed_downloads += 1
            else:
                print(f"     ❌ Failed to download (curl error)")
                failed_downloads += 1
                
        except subprocess.TimeoutExpired:
            print(f"     ❌ Timeout while downloading")
            failed_downloads += 1
        except Exception as e:
            print(f"     ❌ Error: {e}")
            failed_downloads += 1
        
        # Add delay between requests to avoid rate limiting
        if i < len(media_ids):
            time.sleep(1)
    
    print(f"\n📊 Media Info Download Summary:")
    print(f"✅ Successful downloads: {successful_downloads}")
    print(f"❌ Failed downloads: {failed_downloads}")
    print(f"📁 Files saved to: {media_info_dir}/")
    
    return successful_downloads, failed_downloads

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
    
    print(f"\n📋 Downloading all media from media info JSONs")
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

def main():
    """Main function to run the complete workflow"""
    
    print("🚀 Complete Instagram Media Downloader")
    print("=" * 60)
    
    # Step 1: Extract media IDs
    print("📋 Step 1: Extracting media IDs...")
    media_ids = extract_media_ids()
    
    if not media_ids:
        print("❌ No media IDs found. Exiting.")
        return
    
    # Step 2: Download media info JSONs
    print("\n📋 Step 2: Downloading media info JSONs...")
    successful_info, failed_info = download_media_info(media_ids)
    
    if successful_info == 0:
        print("❌ No media info files downloaded. Exiting.")
        return
    
    # Step 3: Download all media
    print("\n📋 Step 3: Downloading all media...")
    download_all_media()
    
    print("\n🎉 Complete workflow finished!")
    print("=" * 60)

if __name__ == "__main__":
    main()
