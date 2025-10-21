# instagram_api.py
import requests
import json
import os

def load_session_cookies():
    """
    Load cookies from the saved session files.
    Returns a dictionary with cookie string and csrftoken.
    """
    cookies_str = ""
    csrftoken = ""
    
    # Try to load from session_data.json first (more reliable)
    if os.path.exists('session_data.json'):
        try:
            with open('session_data.json', 'r') as f:
                session_data = json.load(f)
                csrftoken = session_data.get('csrftoken', '')
                sessionid = session_data.get('sessionid', '')
                ds_user_id = session_data.get('ds_user_id', '')
                mid = session_data.get('mid', '')
                
                # Build cookie string from session data
                cookies_str = f"csrftoken={csrftoken}; sessionid={sessionid}; ds_user_id={ds_user_id}; mid={mid}"
                print(f"✓ Loaded session cookies from session_data.json")
                return cookies_str, csrftoken
        except Exception as e:
            print(f"⚠️ Error loading session_data.json: {e}")
    
    # Fallback to instagram_cookies.json
    if os.path.exists('instagram_cookies.json'):
        try:
            with open('instagram_cookies.json', 'r') as f:
                cookies_data = json.load(f)
                
                # Extract relevant cookies
                cookie_parts = []
                for cookie in cookies_data:
                    name = cookie.get('name', '')
                    value = cookie.get('value', '')
                    
                    if name == 'csrftoken':
                        csrftoken = value
                    elif name in ['sessionid', 'ds_user_id', 'mid', 'datr', 'ig_did']:
                        cookie_parts.append(f"{name}={value}")
                
                cookies_str = "; ".join(cookie_parts)
                if csrftoken:
                    cookies_str = f"csrftoken={csrftoken}; {cookies_str}"
                
                print(f"✓ Loaded session cookies from instagram_cookies.json")
                return cookies_str, csrftoken
        except Exception as e:
            print(f"⚠️ Error loading instagram_cookies.json: {e}")
    
    # If no session files found, return empty strings
    print("⚠️ No session files found, using empty cookies")
    return "", ""

def download_instagram_media(media_id, save_file=True):
    """
    Downloads Instagram media info JSON for a given media_id.
    
    Args:
        media_id (str): The Instagram media ID (from post URL or API response).
        save_file (bool): Whether to save the JSON to a file.
        
    Returns:
        dict: The JSON response as a Python dictionary.
    """
    
    # Load cookies from saved session files
    cookies_str, csrftoken = load_session_cookies()
    
    if not cookies_str or not csrftoken:
        print("❌ No valid session cookies found. Please run the scraper first to login.")
        return None

    url = f'https://www.instagram.com/api/v1/media/{media_id}/info/'

    headers = {
        'Cookie': cookies_str,
        'X-Csrftoken': csrftoken,
        'X-Ig-App-Id': '936619743392459',  # Instagram's official app ID - safe to hardcode
        'X-Requested-With': 'XMLHttpRequest',  # Standard AJAX header - safe to hardcode
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Referer': f'https://www.instagram.com/p/{media_id}/?img_index=1',
        'Sec-Ch-Prefers-Color-Scheme': 'dark'
    }

    # Perform the request
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Optionally save to file
    if save_file:
        with open(f'media_info_{media_id}.json', 'w', encoding='utf-8') as f:
            f.write(response.text)

    # Return parsed JSON
    try:
        return response.json()
    except json.JSONDecodeError:
        print("Warning: Response is not valid JSON.")
        return None


if __name__ == "__main__":
    print("Testing dynamic cookie loading...")
    media_id = '3743025413383934031'  # example from your request
    data = download_instagram_media(media_id)
    if data:
        print("✓ Successfully downloaded media info using dynamic cookies")
        print(json.dumps(data, indent=2))
    else:
        print("❌ Failed to download media info")
