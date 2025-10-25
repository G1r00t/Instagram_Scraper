#!/usr/bin/env python3
"""
Extract media IDs from multiple_pages_result.json
This script finds all unique media IDs from the pagination results
"""

import json
import os

def extract_media_ids():
    """Extract all unique media IDs from multiple_pages_result.json"""
    
    json_file = 'multiple_pages_result.json'
    if not os.path.exists(json_file):
        print(f"❌ Error: {json_file} not found!")
        return
    
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
                        print(f"📸 Found media ID: {post['pk']}")
    elif isinstance(data, dict) and 'posts' in data:
        # Handle case where data is a single object with posts
        for post in data['posts']:
            if 'pk' in post:
                media_ids.add(post['pk'])
                print(f"📸 Found media ID: {post['pk']}")
    
    # Convert set to list and sort
    media_ids_list = sorted(list(media_ids))
    
    print(f"\n📊 Summary:")
    print(f"   Total unique media IDs found: {len(media_ids_list)}")
    
    # Save to file
    output_file = 'extracted_media_ids.txt'
    with open(output_file, 'w') as f:
        for media_id in media_ids_list:
            f.write(f"{media_id}\n")
    
    print(f"💾 Media IDs saved to: {output_file}")
    
    # Show first few IDs as preview
    if media_ids_list:
        print(f"\n🔍 Preview (first 5 IDs):")
        for i, media_id in enumerate(media_ids_list[:5]):
            print(f"   {i+1}. {media_id}")
        if len(media_ids_list) > 5:
            print(f"   ... and {len(media_ids_list) - 5} more")
    
    return media_ids_list

if __name__ == "__main__":
    print("🚀 Extracting media IDs from multiple_pages_result.json")
    print("=" * 60)
    extract_media_ids()
