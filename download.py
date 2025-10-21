import os
from json_download import download_instagram_media
import json

with open('captured_requests.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
media_id_list = [req['media_id'] for req in data['raw_requests'] if req['type'] == 'media_info']
save_folder = 'instagram_media_ohneis652_jsons'
os.makedirs(save_folder, exist_ok=True)
save_folder2 = 'instagram_media_ohneis652'
os.makedirs(save_folder2, exist_ok=True)
for media_id in media_id_list:
    media_data = download_instagram_media(media_id, save_file=False)
    if media_data is not None:
        file_path = os.path.join(save_folder, f'media_info_{media_id}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(media_data, ensure_ascii=False, indent=4))
        print(f'Downloaded {file_path}')
    else:
        print(f"Failed to download media info for {media_id}")


import json
import os
import requests
from urllib.parse import urlparse

# Directory containing downloaded JSON files
json_dir = 'instagram_media_ohneis652_jsons'
# Folder to save downloaded images/videos
save_folder = 'instagram_media_ohneis652'

os.makedirs(save_folder, exist_ok=True)

# Load and aggregate URLs from all JSON files in the directory
def fetch_urls(obj):
    urls = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if 'profile_pic' in k:
                continue
            if k == 'url' and isinstance(v, str):
                urls.append(v)
            else:
                urls.extend(fetch_urls(v))
    elif isinstance(obj, list):
        for item in obj:
            urls.extend(fetch_urls(item))
    return urls

all_urls = []
for name in os.listdir(json_dir):
    if not name.endswith('.json'):
        continue
    path = os.path.join(json_dir, name)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_urls.extend(fetch_urls(data))
        print(f"Scanned {name}")
    except Exception as e:
        print(f"Failed to read {path}: {e}")

print(f"Found {len(all_urls)} URLs across JSON files.")

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
    ext = url.split('?')[0].split('.')[-1]
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

