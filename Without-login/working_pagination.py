#!/usr/bin/env python3
"""
Instagram REST API Pagination - Working Solution
Uses REST API instead of GraphQL (which is currently broken)
Uses cookies from instagram_data_output/cookies.json
"""

import requests
import json
import os

def load_cookies_from_file():
    """Load cookies from instagram_data_output/cookies.json"""
    cookies_file = "instagram_data_output/cookies.json"
    
    if not os.path.exists(cookies_file):
        print(f"❌ Error: {cookies_file} not found. Please run browser_automation.py first.")
        return None, None, None
    
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
        
        return cookies_string, csrf_token, profile_name
        
    except Exception as e:
        print(f"❌ Error loading cookies: {e}")
        return None, None, None

def load_user_id_from_file():
    """Load user ID from instagram_data_output/user_ids.txt"""
    user_ids_file = "instagram_data_output/user_ids.txt"
    
    if not os.path.exists(user_ids_file):
        print(f"❌ Error: {user_ids_file} not found. Please run browser_automation.py first.")
        return None
    
    try:
        with open(user_ids_file, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            if ':' in line:
                username, user_id = line.strip().split(': ', 1)
                print(f"✅ Found user ID for {username}: {user_id}")
                return user_id.strip()
        
        print(f"❌ No user ID found in {user_ids_file}")
        return None
        
    except Exception as e:
        print(f"❌ Error loading user ID: {e}")
        return None

def get_next_page_rest_api(username, current_max_id=None):
    """
    Get next page using REST API approach (WORKING METHOD)
    
    Args:
        username: Instagram username (e.g., 'ohneis652')
        current_max_id: Current max_id from previous page (None for first page)
    
    Returns:
        dict: Contains next_max_id, more_available, and posts data
    """
    
    # Load cookies from file
    cookies, csrf_token, profile_name = load_cookies_from_file()
    if not cookies:
        return {'success': False, 'error': 'Failed to load cookies'}
    
    # Load user ID from file
    user_id = load_user_id_from_file()
    if not user_id:
        return {'success': False, 'error': 'Failed to load user ID'}
    
    headers = {
        'Cookie': cookies,
        'X-Csrftoken': csrf_token,
        'X-Ig-App-Id': '936619743392459',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Referer': f'https://www.instagram.com/{username}/',
    }
    
    # REST API endpoint
    url = f'https://www.instagram.com/api/v1/feed/user/{user_id}/'
    
    # Parameters
    params = {'count': 12}
    if current_max_id:
        params['max_id'] = current_max_id
    
    print(f"🔍 Requesting page for {username}")
    if current_max_id:
        print(f"📍 Current max_id: {current_max_id}")
    else:
        print(f"📍 First page (no max_id)")
    print(f"📡 URL: {url}")
    print(f"📋 Parameters: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'items' in data:
                posts = data['items']
                more_available = data.get('more_available', False)
                next_max_id = data.get('next_max_id', None)
                
                print(f"✅ SUCCESS!")
                print(f"📊 Posts in this page: {len(posts)}")
                print(f"🔄 More available: {more_available}")
                print(f"📍 Next max_id: {next_max_id}")
                
                return {
                    'success': True,
                    'posts': posts,
                    'more_available': more_available,
                    'next_max_id': next_max_id,
                    'posts_count': len(posts),
                    'raw_response': data
                }
            else:
                print("❌ No 'items' found in response")
                print(f"Response keys: {list(data.keys())}")
                return {
                    'success': False,
                    'error': 'No items found in response',
                    'raw_response': data
                }
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return {
                'success': False,
                'error': f'HTTP {response.status_code}',
                'raw_response': response.text
            }
            
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return {
            'success': False,
            'error': f'JSON decode error: {e}'
        }

def get_multiple_pages(username, num_pages=3):
    """
    Get multiple pages of posts
    
    Args:
        username: Instagram username
        num_pages: Number of pages to fetch
    
    Returns:
        list: List of page results
    """
    
    print(f"🚀 Getting {num_pages} pages for {username}")
    print("=" * 60)
    
    all_pages = []
    current_max_id = None
    
    for page_num in range(1, num_pages + 1):
        print(f"\n📄 Page {page_num}/{num_pages}")
        print("-" * 40)
        
        result = get_next_page_rest_api(username, current_max_id)
        
        if result['success']:
            all_pages.append(result)
            
            if result['more_available'] and result['next_max_id']:
                current_max_id = result['next_max_id']
                print(f"➡️  Moving to next page with max_id: {current_max_id}")
            else:
                print("🏁 No more pages available")
                break
        else:
            print(f"❌ Failed to get page {page_num}: {result.get('error', 'Unknown error')}")
            break
    
    return all_pages

def main():
    """Test the REST API pagination"""
    
    username = "ohneis652"
    
    print("🚀 Instagram REST API Pagination Test")
    print("=" * 60)
    
    # Test single page
    print("🔍 Test 1: Single page")
    result = get_next_page_rest_api(username)
    
    if result['success']:
        print(f"\n✅ SUCCESS!")
        print(f"Posts: {result['posts_count']}")
        print(f"More available: {result['more_available']}")
        print(f"Next max_id: {result['next_max_id']}")
        
        # Save the result
        with open('rest_api_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("📁 Result saved to: rest_api_result.json")
        
        # Test multiple pages if more are available
        if result['more_available'] and result['next_max_id']:
            print(f"\n🔍 Test 2: Multiple pages")
            pages = get_multiple_pages(username, 20)
            
            print(f"\n📊 Summary:")
            print(f"Total pages fetched: {len(pages)}")
            total_posts = sum(page['posts_count'] for page in pages)
            print(f"Total posts: {total_posts}")
            
            # Save all pages
            with open('multiple_pages_result.json', 'w') as f:
                json.dump(pages, f, indent=2)
            print("📁 All pages saved to: multiple_pages_result.json")
    else:
        print(f"\n❌ FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()