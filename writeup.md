# Instagram Scraper

Started with downloading everything manually

first i was trying to find the html of instagram requests using burpsuite 

now when i turned on the intercept , obviously it is having many get and post requests

And when i click on a video in the proxy browser of burp i get a get request in the intercept panel which looks like this
```bash
GET /o1/v/t2/f2/m86/AQOenTd3E7ui8b7ZBjWjGz84IsUe2sLF-ZY5dUx6qPIMbo6g86yMWMuMJ7Yim_CXziL_Q_icVbisKhplalUuPjCyz8vFgAOXa6ayimo.mp4?_nc_cat=104&_nc_oc=AdkDVJES3srGPB-KkNohnLiRQXkjW93gTjwoHgYVVXxd2ynPO52SUM89YTJpJCVOLjc&_nc_sid=5e9851&_nc_ht=instagram.fjai2-1.fna.fbcdn.net&_nc_ohc=QNtp-H4tyscQ7kNvwF7uRv9&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0xJUFMuQzMuNzIwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6MjQzNzI4NTUyMzU3NDIwMTMsInZpX3VzZWNhc2VfaWQiOjEwMDk5LCJkdXJhdGlvbl9zIjo0MSwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&vs=6808b8760f675941&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC84MDQyQ0RDRkY3NzAwM0VFRDA2MUNDNkVBNjVERkRCNF92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HQVhNalNCZnRCV0E1czBEQUU5cHJ4THdubmtFYnFfRUFBQUYVAgLIARIAKAAYABsCiAd1c2Vfb2lsATEScHJvZ3Jlc3NpdmVfcmVjaXBlATEVAAAm-qTop_K-y1YVAigCQzMsF0BE2p--dsi0GBJkYXNoX2Jhc2VsaW5lXzFfdjERAHX-B2XmnQEA&_nc_gid=An37KX4mFCQhbeEysQ8arg&_nc_zt=28&oh=00_AfeKfc_0FHlz3tILvc9MFyhamBQIqSACRVQjhtEI6l4Drw&oe=68F7D229 HTTP/2
Host: instagram.fjai2-1.fna.fbcdn.net
Sec-Ch-Ua-Platform: "Linux"
Accept-Encoding: gzip, deflate, br
Accept-Language: en-GB,en;q=0.9
Sec-Ch-Ua: "Chromium";v="139", "Not;A=Brand";v="99"
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36
Sec-Ch-Ua-Mobile: ?0
Accept: */*
Sec-Fetch-Site: cross-site
Sec-Fetch-Mode: no-cors
Sec-Fetch-Dest: video
Sec-Fetch-Storage-Access: active
Referer: https://www.instagram.com/
Range: bytes=0-
Priority: i
```


So from this i can automatically download the video using wget like this
```bash
wget -c \
  --header="Referer: https://www.instagram.com/" \
  --header="User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36" \
  --trust-server-names \
  -O instagram_video.mp4 \
  "https://instagram.fjai2-1.fna.fbcdn.net/o1/v/t2/f2/m86/AQOenTd3E7ui8b7ZBjWjGz84IsUe2sLF-ZY5dUx6qPIMbo6g86yMWMuMJ7Yim_CXziL_Q_icVbisKhplalUuPjCyz8vFgAOXa6ayimo.mp4?_nc_cat=104&_nc_oc=AdkDVJES3srGPB-KkNohnLiRQXkjW93gTjwoHgYVVXxd2ynPO52SUM89YTJpJCVOLjc&_nc_sid=5e9851&_nc_ht=instagram.fjai2-1.fna.fbcdn.net&_nc_ohc=QNtp-H4tyscQ7kNvwF7uRv9&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0xJUFMuQzMuNzIwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6MjQzNzI4NTUyMzU3NDIwMTMsInZpX3VzZWNhc2VfaWQiOjEwMDk5LCJkdXJhdGlvbl9zIjo0MSwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&vs=6808b8760f675941&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC84MDQyQ0RDRkY3NzAwM0VFRDA2MUNDNkVBNjVERkRCNF92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HQVhNalNCZnRCV0E1czBEQUU5cHJ4THdubmtFYnFfRUFBQUYVAgLIARIAKAAYABsCiAd1c2Vfb2lsATEScHJvZ3Jlc3NpdmVfcmVjaXBlATEVAAAm-qTop_K-y1YVAigCQzMsF0BE2p--dsi0GBJkYXNoX2Jhc2VsaW5lXzFfdjERAHX-B2XmnQEA&_nc_gid=An37KX4mFCQhbeEysQ8arg&_nc_zt=28&oh=00_AfeKfc_0FHlz3tILvc9MFyhamBQIqSACRVQjhtEI6l4Drw&oe=68F7D229"
```

and when i click on a post which contains multi images i get a request for the info like this
```bash
GET /api/v1/media/3731016507120029101/info/ HTTP/2
Host: www.instagram.com
Cookie: csrftoken=bRAoyOh76Nj8SZR410VBfC; datr=JPn1aN4OMdngSuvxQEBnjdyw; ig_did=BE0B2171-0A0A-434B-A45D-14D4422A9B18; wd=948x927; ig_nrcb=1; mid=aPX5JQAEAAH3KVYSzOrc1uZ8JPVe; sessionid=77402749614%3AsvEshRW4SmC9Ap%3A14%3AAYgQuZlwJwAZRPp96EdcQ1X1zPyY7lCG2epGgIb8rA; ds_user_id=77402749614; ps_l=1; ps_n=1; rur="EAG\05477402749614\0541792488946:01feb59e4e385eca87876beaddc5f087269ba361aadc7c8da521e4af6637c96f83db306b"
Sec-Ch-Ua-Full-Version-List: 
Sec-Ch-Ua-Platform: "Linux"
Sec-Ch-Ua: "Chromium";v="139", "Not;A=Brand";v="99"
Sec-Ch-Ua-Model: ""
Sec-Ch-Ua-Mobile: ?0
X-Ig-App-Id: 936619743392459
X-Requested-With: XMLHttpRequest
Accept: */*
X-Csrftoken: bRAoyOh76Nj8SZR410VBfC
X-Web-Session-Id: 0yx937:nnxp26:gc2zyt
Accept-Language: en-GB,en;q=0.9
X-Asbd-Id: 359341
Sec-Ch-Prefers-Color-Scheme: dark
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36
X-Ig-Www-Claim: hmac.AR01mKS2gTDeuJHlFaLch4KbFaLfNunCo9tAN3FHRw72mJP5
Sec-Ch-Ua-Platform-Version: ""
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://www.instagram.com/p/DPHO77WAg2t/?img_index=1
Accept-Encoding: gzip, deflate, br
Priority: u=1, i
```


so i download the media_info.json which contains the images like this
```bash
curl 'https://www.instagram.com/api/v1/media/3731016507120029101/info/' \
  -H 'Cookie: csrftoken=bRAoyOh76Nj8SZR410VBfC; datr=JPn1aN4OMdngSuvxQEBnjdyw; ig_did=BE0B2171-0A0A-434B-A45D-14D4422A9B18; wd=948x927; ig_nrcb=1; mid=aPX5JQAEAAH3KVYSzOrc1uZ8JPVe; sessionid=77402749614%3AsvEshRW4SmC9Ap%3A14%3AAYgQuZlwJwAZRPp96EdcQ1X1zPyY7lCG2epGgIb8rA; ds_user_id=77402749614; ps_l=1; ps_n=1; rur="EAG\05477402749614\0541792488946:01feb59e4e385eca87876beaddc5f087269ba361aadc7c8da521e4af6637c96f83db306b"' \
  -H 'X-Csrftoken: bRAoyOh76Nj8SZR410VBfC' \
  -H 'X-Ig-App-Id: 936619743392459' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'Accept: */*' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36' \
  -H 'Referer: https://www.instagram.com/p/DPHO77WAg2t/?img_index=1' \
  -H 'Accept-Language: en-GB,en;q=0.9' \
  --compressed \
  -o media_info.json
```

and from the media_info.json i got the urls of all images in the post so i download them like this
```python
import json
import os
import requests
from urllib.parse import urlparse

# Path to your downloaded JSON
json_file = 'media_info.json'
# Folder to save downloaded images/videos
save_folder = 'instagram_media'

os.makedirs(save_folder, exist_ok=True)

# Load JSON
with open(json_file, 'r') as f:
    data = json.load(f)


# Recursively fetch all URLs, skipping profile_pic_url
# Recursively fetch all URLs, skipping any key containing 'profile_pic'
def fetch_urls(obj):
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


all_urls = fetch_urls(data)
print(f"Found {len(all_urls)} URLs in JSON.")

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

print(f"{len(downloaded_urls)} unique media to download.")

# Download each unique media
for i, url in enumerate(downloaded_urls, 1):
    ext = url.split('?')[0].split('.')[-1]  # extension
    filename = os.path.join(save_folder, f'media_{i}.{ext}')
    print(f"Downloading {url} -> {filename}")
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

print("All unique media downloaded.")
```

So now i created a browser automation using patchright (the patched version of playwright) with the help of claude , I implemented some human like features in that like small chunk scrolling , pauses , random mouse movements , etc.

Workflow:

Browser opens (visible window)
It logins automatically
Scraper navigates to profile with human-like behavior
Scrolls and collects posts naturally
Opens each post and captures network requests
Saves everything to captured_requests.json

From these requests i download the media_info.json using this
```python
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

```

Then from this media_info.json files we can easily download the data as stated above



The overall workflow 


Patchright opens a browser -> it logs your account in-> Then the profile is fetched -> then media ids are fethced one by one -> media_info.json is downloaded from those media ids -> images/videos are now can be downloaded from this json 


