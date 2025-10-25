#!/usr/bin/env python3
"""
Download media info for extracted media IDs
This script downloads media info JSONs for all IDs in extracted_media_ids.txt
Uses cookies from instagram_data_output/cookies.json
"""

import json
import os
import subprocess
import time

def load_cookies_from_file():
    """Load cookies from instagram_data_output/cookies.json"""
    cookies_file = "instagram_data_output/cookies.json"
    
    if not os.path.exists(cookies_file):
        print(f"❌ Error: {cookies_file} not found. Please run browser_automation.py first.")
        return None, None, None, None
    
    try:
        with open(cookies_file, 'r') as f:
            cookies_data = json.load(f)
        
        # Get the first profile's cookies
        profile_name = list(cookies_data.keys())[0]
        profile_cookies = cookies_data[profile_name]
        
        # Extract important cookies
        csrf_token = profile_cookies.get('csrftoken', {}).get('value', '')
        sessionid = profile_cookies.get('sessionid', {}).get('value', '')
        ds_user_id = profile_cookies.get('ds_user_id', {}).get('value', '')
        datr = profile_cookies.get('datr', {}).get('value', '')
        ig_did = profile_cookies.get('ig_did', {}).get('value', '')
        mid = profile_cookies.get('mid', {}).get('value', '')
        wd = profile_cookies.get('wd', {}).get('value', '')
        ig_nrcb = profile_cookies.get('ig_nrcb', {}).get('value', '')
        
        # Build cookie string
        cookie_parts = []
        if csrf_token:
            cookie_parts.append(f'csrftoken={csrf_token}')
        if sessionid:
            cookie_parts.append(f'sessionid={sessionid}')
        if ds_user_id:
            cookie_parts.append(f'ds_user_id={ds_user_id}')
        if datr:
            cookie_parts.append(f'datr={datr}')
        if ig_did:
            cookie_parts.append(f'ig_did={ig_did}')
        if mid:
            cookie_parts.append(f'mid={mid}')
        if wd:
            cookie_parts.append(f'wd={wd}')
        if ig_nrcb:
            cookie_parts.append(f'ig_nrcb={ig_nrcb}')
        
        cookies_string = '; '.join(cookie_parts)
        
        print(f"✅ Loaded cookies for profile: {profile_name}")
        print(f"🔑 Found {len(cookie_parts)} cookies")
        
        return cookies_string, csrf_token, ds_user_id, profile_name
        
    except Exception as e:
        print(f"❌ Error loading cookies: {e}")
        return None, None, None, None

def download_media_info():
    """Download media info JSON files for all media IDs"""
    
    # Load cookies from file
    cookies, csrf_token, ds_user_id, profile_name = load_cookies_from_file()
    if not cookies:
        return
    
    # Read media IDs from file
    media_ids_file = "extracted_media_ids.txt"
    if not os.path.exists(media_ids_file):
        print(f"❌ Error: {media_ids_file} not found. Please run extract_media_ids.py first.")
        return
    
    with open(media_ids_file, "r") as f:
        media_ids = [line.strip() for line in f.readlines() if line.strip()]
    
    print(f"📋 Found {len(media_ids)} media IDs to download")
    print("=" * 60)
    
    # Create directory for media info files
    media_info_dir = "media_info"
    os.makedirs(media_info_dir, exist_ok=True)
    
    # Authentication tokens
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
            '-H', f'Referer: https://www.instagram.com/{profile_name}/',
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
    
    print(f"\n📊 Download Summary:")
    print(f"✅ Successful downloads: {successful_downloads}")
    print(f"❌ Failed downloads: {failed_downloads}")
    print(f"📁 Files saved to: {media_info_dir}/")

if __name__ == "__main__":
    print("🚀 Downloading media info for extracted media IDs")
    print("=" * 60)
    download_media_info()
