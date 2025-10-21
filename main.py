import asyncio
import json
import random
import os
import sys
import re
from typing import List, Dict, Set
from patchright.async_api import async_playwright
from datetime import datetime

class Logger:
    """Dual output - console and file"""
    def __init__(self, filename='scraper_log.txt'):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
        self.log.write(f"Instagram Scraper Log - {datetime.now().isoformat()}\n")
        self.log.write("="*80 + "\n\n")
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    
    def close(self):
        self.log.close()


class HumanBehavior:
    """Simulates realistic human browsing patterns"""
    
    @staticmethod
    async def random_delay(min_ms=800, max_ms=2500):
        """Random delay to mimic human reading/thinking time"""
        await asyncio.sleep(random.uniform(min_ms/1000, max_ms/1000))
    
    @staticmethod
    async def human_scroll(page, distance=None):
        """Smooth human-like scrolling"""
        if distance is None:
            distance = random.randint(300, 700)
        
        # Scroll in small chunks for realistic effect
        chunks = random.randint(3, 6)
        chunk_size = distance // chunks
        
        for _ in range(chunks):
            await page.evaluate(f'window.scrollBy(0, {chunk_size})')
            await asyncio.sleep(random.uniform(0.05, 0.15))
        
        # Random pause after scroll (human reading time)
        await HumanBehavior.random_delay(1000, 2000)
    
    @staticmethod
    async def mouse_movement(page):
        """Simulate random mouse movements"""
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        
        await page.mouse.move(x, y, steps=random.randint(5, 15))
        await asyncio.sleep(random.uniform(0.1, 0.3))
    
    @staticmethod
    async def random_pause():
        """Random pause like human getting distracted"""
        if random.random() < 0.15:  # 15% chance of longer pause
            await asyncio.sleep(random.uniform(3, 6))


class InstagramScraper:
    def __init__(self, cookies_file='instagram_cookies.json'):
        self.cookies_file = cookies_file
        self.browser = None
        self.context = None
        self.page = None
        self.collected_posts = []
        self.request_data = []
        self.media_info_cache = {}
        self.captured_media = {}  # Store media by shortcode
        
    async def setup_browser(self):
        """Initialize browser with anti-detection measures"""
        playwright = await async_playwright().start()
        
        # Launch with realistic browser profile
        self.browser = await playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-infobars',
                '--window-size=1920,1080',
                '--start-maximized',
            ]
        )
        
        # Create context with realistic viewport and user agent
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='Asia/Kolkata',
            geolocation={'latitude': 26.9124, 'longitude': 75.7873},
            permissions=['geolocation'],
        )
        
        # Load cookies if they exist
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
                await self.context.add_cookies(cookies)
            print("✓ Loaded existing cookies")
        
        self.page = await self.context.new_page()
        
        # Inject scripts to avoid detection
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            window.chrome = {
                runtime: {}
            };
        """)
        
        print("✓ Browser setup complete")
    
    async def human_type(self, element, text, mistake_chance=0.1):
        """Type text with human-like behavior including mistakes"""
        for i, char in enumerate(text):
            # Random chance of making a typo
            if random.random() < mistake_chance and i > 0:
                # Type wrong character
                wrong_chars = 'abcdefghijklmnopqrstuvwxyz'
                wrong_char = random.choice(wrong_chars)
                await element.type(wrong_char, delay=random.randint(80, 150))
                await asyncio.sleep(random.uniform(0.2, 0.5))
                
                # Realize mistake and delete
                await self.page.keyboard.press('Backspace')
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Type the correct character
            delay = random.randint(80, 250)
            
            # Slower for first few characters (getting started)
            if i < 3:
                delay = random.randint(150, 300)
            
            # Occasional pause mid-typing (thinking)
            if random.random() < 0.1:
                await asyncio.sleep(random.uniform(0.3, 0.8))
            
            await element.type(char, delay=delay)
        
        # Brief pause after finishing typing
        await asyncio.sleep(random.uniform(0.3, 0.7))
    
    async def automated_login(self, username, password):
        """Automated human-like login"""
        print("\n🔐 Starting automated login...")
        
        try:
            # Go to Instagram
            await self.page.goto('https://www.instagram.com/', wait_until='domcontentloaded')
            print("  ✓ Loaded Instagram homepage")
            
            # Random human-like delay before interacting
            await HumanBehavior.random_delay(2000, 4000)
            
            # Move mouse randomly (human behavior before login)
            await HumanBehavior.mouse_movement(self.page)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Wait for and find username input
            try:
                username_input = await self.page.wait_for_selector(
                    'input[name="username"]', 
                    timeout=10000
                )
                print("  ✓ Found username field")
            except:
                print("  ⚠️  Username field not found, trying alternative selector...")
                username_input = await self.page.wait_for_selector(
                    'input[aria-label*="username" i]',
                    timeout=10000
                )
            
            # Click username field (with mouse movement)
            await HumanBehavior.mouse_movement(self.page)
            await username_input.click()
            await asyncio.sleep(random.uniform(0.3, 0.7))
            
            # Type username with human-like behavior
            print("  ⌨️  Typing username...")
            await self.human_type(username_input, username, mistake_chance=0.05)
            
            # Random pause before moving to password
            await asyncio.sleep(random.uniform(0.5, 1.2))
            
            # Find password input
            password_input = await self.page.wait_for_selector(
                'input[name="password"]',
                timeout=5000
            )
            
            # Move mouse and click password field
            await HumanBehavior.mouse_movement(self.page)
            await password_input.click()
            await asyncio.sleep(random.uniform(0.3, 0.7))
            
            # Type password with human-like behavior
            print("  ⌨️  Typing password...")
            await self.human_type(password_input, password, mistake_chance=0.03)
            
            # Random pause before clicking login
            await asyncio.sleep(random.uniform(0.8, 1.5))
            
            # Move mouse around (hesitation)
            await HumanBehavior.mouse_movement(self.page)
            await asyncio.sleep(random.uniform(0.3, 0.7))
            
            # Find and click login button
            login_button_selectors = [
                'button[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Log In")',
                'div[role="button"]:has-text("Log in")'
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = await self.page.wait_for_selector(selector, timeout=2000)
                    if login_button:
                        break
                except:
                    continue
            
            if not login_button:
                print("  ⚠️  Could not find login button")
                return False
            
            print("  🖱️  Clicking login button...")
            await login_button.click()
            
            # Wait for navigation/login to process
            await asyncio.sleep(5)
            
            # Check for various post-login scenarios
            current_url = self.page.url
            
            # Handle "Save Login Info" prompt
            try:
                save_info_buttons = await self.page.query_selector_all('button')
                for button in save_info_buttons:
                    text = await button.inner_text()
                    if text and 'not now' in text.lower():
                        print("  ⚠️  'Save Login Info' prompt detected, clicking 'Not Now'...")
                        await asyncio.sleep(random.uniform(1, 2))
                        await button.click()
                        await asyncio.sleep(2)
                        break
            except:
                pass
            
            # Handle "Turn on Notifications" prompt
            try:
                notification_buttons = await self.page.query_selector_all('button')
                for button in notification_buttons:
                    text = await button.inner_text()
                    if text and 'not now' in text.lower():
                        print("  ⚠️  'Notifications' prompt detected, clicking 'Not Now'...")
                        await asyncio.sleep(random.uniform(1, 2))
                        await button.click()
                        await asyncio.sleep(2)
                        break
            except:
                pass
            
            # Check if login was successful
            await asyncio.sleep(3)
            
            # Verify login by checking for profile/home elements
            try:
                # Look for elements that only appear when logged in
                await self.page.wait_for_selector(
                    'svg[aria-label="Home"], svg[aria-label="Search"], a[href*="/direct/"]',
                    timeout=10000
                )
                print("  ✅ Login successful!")
                
                # Save cookies
                cookies = await self.context.cookies()
                with open(self.cookies_file, 'w') as f:
                    json.dump(cookies, f, indent=2)
                print("  ✓ Cookies saved")
                
                # Extract session data
                session_data = {}
                for cookie in cookies:
                    if cookie['name'] in ['sessionid', 'csrftoken', 'ds_user_id', 'mid']:
                        session_data[cookie['name']] = cookie['value']
                
                with open('session_data.json', 'w') as f:
                    json.dump(session_data, f, indent=2)
                print("  ✓ Session data saved")
                
                return session_data
                
            except:
                print("  ❌ Login may have failed or requires additional verification")
                print("  🔍 Current URL:", current_url)
                
                # Check for error messages
                try:
                    error_element = await self.page.query_selector('p[role="alert"]')
                    if error_element:
                        error_text = await error_element.inner_text()
                        print(f"  ⚠️  Error message: {error_text}")
                except:
                    pass
                
                # Check if it's a 2FA/checkpoint
                if 'challenge' in current_url or 'two_factor' in current_url:
                    print("\n" + "="*60)
                    print("⚠️  TWO-FACTOR AUTHENTICATION REQUIRED")
                    print("="*60)
                    print("Instagram requires additional verification.")
                    print("Please complete the verification in the browser window.")
                    print("Press ENTER when you've completed verification...")
                    print("="*60 + "\n")
                    input()
                    
                    # Save cookies after manual verification
                    cookies = await self.context.cookies()
                    with open(self.cookies_file, 'w') as f:
                        json.dump(cookies, f, indent=2)
                    
                    session_data = {}
                    for cookie in cookies:
                        if cookie['name'] in ['sessionid', 'csrftoken', 'ds_user_id', 'mid']:
                            session_data[cookie['name']] = cookie['value']
                    
                    with open('session_data.json', 'w') as f:
                        json.dump(session_data, f, indent=2)
                    
                    return session_data
                
                return False
        
        except Exception as e:
            print(f"  ❌ Login error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def check_login_status(self):
        """Check if already logged in"""
        await self.page.goto('https://www.instagram.com/', wait_until='domcontentloaded')
        await HumanBehavior.random_delay(2000, 3000)
        
        try:
            await self.page.wait_for_selector('input[name="username"]', timeout=3000)
            return False
        except:
            return True
    
    def extract_media_urls(self, media_data):
        """Extract all video and image URLs from media info response"""
        urls = {
            'videos': [],
            'images': []
        }
        
        def traverse(obj, path=""):
            if isinstance(obj, dict):
                if 'profile_pic' in path:
                    return
                
                # Look for video versions (highest quality)
                if 'video_versions' in obj and isinstance(obj['video_versions'], list):
                    for video in obj['video_versions']:
                        if 'url' in video:
                            url = video['url']
                            # Get complete URL (not fragmented DASH)
                            if '.mp4' in url and 'bytestart' not in url:
                                urls['videos'].append({
                                    'url': url,
                                    'width': video.get('width'),
                                    'height': video.get('height'),
                                    'type': video.get('type')
                                })
                
                # Look for image versions
                if 'image_versions2' in obj:
                    candidates = obj['image_versions2'].get('candidates', [])
                    if candidates and len(candidates) > 0:
                        img = candidates[0]
                        if 'url' in img:
                            urls['images'].append({
                                'url': img['url'],
                                'width': img.get('width'),
                                'height': img.get('height')
                            })
                
                # Handle carousel media
                if 'carousel_media' in obj:
                    for item in obj['carousel_media']:
                        traverse(item, path + '.carousel')
                
                for key, value in obj.items():
                    traverse(value, path + f'.{key}')
            
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item, path)
        
        traverse(media_data)
        
        # Remove duplicates
        urls['videos'] = list({v['url']: v for v in urls['videos']}.values())
        urls['images'] = list({i['url']: i for i in urls['images']}.values())
        
        return urls
    
    async def setup_request_interception(self):
        """Intercept network requests for media URLs"""
        
        async def handle_route(route):
            request = route.request
            url = request.url
            
            # Intercept media info API calls
            if '/api/v1/media/' in url and '/info/' in url:
                print(f"  📡 API call intercepted: {url[:80]}...")
                
                response = await route.fetch()
                body = await response.text()
                
                try:
                    data = json.loads(body)
                    media_id = url.split('/media/')[1].split('/')[0]
                    
                    media_urls = self.extract_media_urls(data)
                    
                    self.media_info_cache[media_id] = {
                        'raw_data': data,
                        'extracted_urls': media_urls,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    print(f"    ✓ Videos: {len(media_urls['videos'])}, Images: {len(media_urls['images'])}")
                    
                    self.request_data.append({
                        'type': 'media_info',
                        'media_id': media_id,
                        'url': url,
                        'headers': dict(request.headers),
                        'media_urls': media_urls,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    print(f"    ⚠️  Parse error: {e}")
                
                await route.continue_()
                return
            
            await route.continue_()
        
        await self.page.route('**/*', handle_route)
        print("✓ Request interception enabled")
    
    async def navigate_to_profile(self, username):
        """Navigate to Instagram profile"""
        print(f"\n🎯 Navigating to profile: @{username}")
        
        url = f'https://www.instagram.com/{username}/'
        await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        await HumanBehavior.random_delay(2000, 3500)
        
        try:
            await self.page.wait_for_selector('main', timeout=5000)
            print("✓ Profile loaded")
        except:
            print("❌ Profile not found")
            raise Exception(f"Profile @{username} not found")
    
    async def extract_post_shortcodes(self, max_posts=None):
        """Extract post shortcodes with proper limit enforcement"""
        print(f"\n📋 Extracting post shortcodes (limit: {max_posts or 'all'})...")
        
        shortcodes = []
        previous_count = 0
        no_new_posts_count = 0
        scroll_count = 0
        
        while True:
            # Extract visible post links
            post_links = await self.page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
            
            for link in post_links:
                # Stop if we've reached the limit
                if max_posts and len(shortcodes) >= max_posts:
                    break
                
                href = await link.get_attribute('href')
                if href:
                    # Extract shortcode from both /p/ and /reel/ URLs
                    match = re.search(r'/(p|reel)/([^/]+)', href)
                    if match:
                        shortcode = match.group(2)
                        if shortcode and shortcode not in shortcodes:
                            shortcodes.append(shortcode)
                            print(f"  ✓ Found post: {shortcode}")
            
            current_count = len(shortcodes)
            
            # Check if we've reached the target
            if max_posts and current_count >= max_posts:
                print(f"✓ Reached target of {max_posts} posts")
                break
            
            # Check if new posts were found
            if current_count == previous_count:
                no_new_posts_count += 1
                print(f"  ⚠️  No new posts found (attempt {no_new_posts_count}/3)")
                
                if no_new_posts_count >= 3:
                    print("✓ No more posts available")
                    break
            else:
                no_new_posts_count = 0
            
            previous_count = current_count
            
            # Human-like scrolling
            await HumanBehavior.human_scroll(self.page)
            scroll_count += 1
            
            await HumanBehavior.random_pause()
            
            if scroll_count % 5 == 0:
                print(f"  💭 Taking a break...")
                await asyncio.sleep(random.uniform(2, 4))
        
        print(f"\n✓ Total posts collected: {len(shortcodes)}")
        self.collected_posts = shortcodes
        return shortcodes
    
    async def fetch_media_via_api(self, shortcode):
        """Fetch media info directly via API call"""
        print(f"  🔍 Fetching media ID from shortcode...")
        
        try:
            # Get the page HTML to extract media ID
            post_url = f'https://www.instagram.com/p/{shortcode}/'
            
            # Navigate and wait for content
            await self.page.goto(post_url, wait_until='domcontentloaded', timeout=45000)
            await asyncio.sleep(2)  # Wait for JS to execute
            
            # Extract media ID from page scripts
            page_content = await self.page.content()
            
            # Look for media_id in various places
            media_id = None
            
            # Method 1: Look in script tags
            scripts = await self.page.query_selector_all('script')
            for script in scripts:
                content = await script.inner_text()
                if 'media_id' in content:
                    match = re.search(r'"media_id":"(\d+)"', content)
                    if match:
                        media_id = match.group(1)
                        break
            
            if not media_id:
                # Method 2: Extract from the shortcode_media object
                match = re.search(r'"shortcode_media".*?"id":"(\d+)"', page_content)
                if match:
                    media_id = match.group(1)
            
            if media_id:
                print(f"    ✓ Found media ID: {media_id}")
                
                # Now make the API call
                api_url = f'https://www.instagram.com/api/v1/media/{media_id}/info/'
                
                # This navigation will trigger our interceptor
                response = await self.page.evaluate(f"""
                    fetch('{api_url}', {{
                        credentials: 'include',
                        headers: {{
                            'X-Requested-With': 'XMLHttpRequest'
                        }}
                    }})
                """)
                
                await asyncio.sleep(1)  # Give time for interceptor to work
                
                return True
            else:
                print(f"    ⚠️  Could not extract media ID")
                return False
                
        except Exception as e:
            print(f"    ⚠️  API fetch failed: {e}")
            return False
    
    async def open_and_capture_post(self, shortcode):
        """Open individual post and capture media"""
        print(f"\n🔍 Opening post: {shortcode}")
        
        post_url = f'https://www.instagram.com/p/{shortcode}/'
        
        await HumanBehavior.mouse_movement(self.page)
        await HumanBehavior.random_delay(500, 1000)
        
        try:
            # Navigate to post
            await self.page.goto(post_url, wait_until='domcontentloaded', timeout=45000)
            
            # Wait for media to load
            await asyncio.sleep(3)
            
            # Try to fetch via API
            await self.fetch_media_via_api(shortcode)
            
            # Scroll to see caption
            await HumanBehavior.human_scroll(self.page, distance=random.randint(100, 300))
            
            # Try to find and click through carousel
            try:
                next_buttons = await self.page.query_selector_all('button[aria-label*="Next"]')
                if next_buttons and len(next_buttons) > 0:
                    print("  📸 Carousel detected, browsing...")
                    clicks = min(random.randint(2, 4), len(next_buttons))
                    for i in range(clicks):
                        await HumanBehavior.random_delay(1500, 2500)
                        try:
                            await next_buttons[0].click()
                            await asyncio.sleep(1)
                            print(f"    Slide {i+2}")
                        except:
                            break
            except:
                pass
            
            await HumanBehavior.random_delay(1500, 2500)
            print(f"  ✓ Post captured")
            
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
    
    async def scrape_profile(self, profile_username, max_posts=None, login_username=None, login_password=None):
        """Main scraping function"""
        try:
            await self.setup_browser()
            
            # Check if already logged in
            logged_in = await self.check_login_status()
            
            if not logged_in:
                print("❌ Not logged in")
                
                # Try automated login if credentials provided
                if login_username and login_password:
                    session_data = await self.automated_login(login_username, login_password)
                    if not session_data:
                        print("⚠️  Automated login failed, you may need to login manually")
                        return None, []
                else:
                    print("⚠️  No login credentials provided")
                    return None, []
            else:
                print("✓ Already logged in")
                if os.path.exists('session_data.json'):
                    with open('session_data.json', 'r') as f:
                        session_data = json.load(f)
                else:
                    session_data = {}
            
            await self.setup_request_interception()
            await self.navigate_to_profile(profile_username)
            
            # Extract EXACTLY max_posts shortcodes
            shortcodes = await self.extract_post_shortcodes(max_posts)
            
            # Visit each post
            print(f"\n🎬 Visiting {len(shortcodes)} posts...")
            for i, shortcode in enumerate(shortcodes, 1):
                print(f"\n[{i}/{len(shortcodes)}]", end=" ")
                await self.open_and_capture_post(shortcode)
                
                # Go back
                await self.page.go_back(wait_until='domcontentloaded', timeout=30000)
                await HumanBehavior.random_delay(1500, 2500)
            
            self.save_captured_data()
            
            print("\n" + "="*60)
            print("✅ SCRAPING COMPLETE")
            print(f"📊 Posts processed: {len(shortcodes)}")
            print(f"📡 Requests captured: {len(self.request_data)}")
            print(f"💾 Saved to: captured_requests.json")
            print(f"📝 Log: scraper_log.txt")
            print("="*60 + "\n")
            
            return session_data, self.request_data
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.browser:
                await self.browser.close()
    
    def save_captured_data(self):
        """Save captured request data to file"""
        downloadable_media = []
        
        for req in self.request_data:
            if req['type'] == 'media_info' and 'media_urls' in req:
                media_urls = req['media_urls']
                
                for video in media_urls['videos']:
                    downloadable_media.append({
                        'type': 'video',
                        'url': video['url'],
                        'width': video['width'],
                        'height': video['height'],
                        'media_id': req['media_id']
                    })
                
                for image in media_urls['images']:
                    downloadable_media.append({
                        'type': 'image',
                        'url': image['url'],
                        'width': image['width'],
                        'height': image['height'],
                        'media_id': req['media_id']
                    })
        
        output = {
            'posts_collected': self.collected_posts,
            'total_posts': len(self.collected_posts),
            'total_media': len(downloadable_media),
            'downloadable_media': downloadable_media,
            'raw_requests': self.request_data,
            'timestamp': datetime.now().isoformat()
        }
        
        with open('captured_requests.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Saved to captured_requests.json")
        print(f"   - Media items: {len(downloadable_media)}")
        print(f"   - Videos: {sum(1 for m in downloadable_media if m['type'] == 'video')}")
        print(f"   - Images: {sum(1 for m in downloadable_media if m['type'] == 'image')}")


async def main():
    logger = Logger('scraper_log.txt')
    sys.stdout = logger
    
    try:
        scraper = InstagramScraper()
        
        # Get login credentials
        print("="*60)
        print("INSTAGRAM PROFILE SCRAPER")
        print("="*60)
        
        # Login credentials - hardcoded
        login_username = "kamehameha149"
        login_password = "vT8#pLx1zQe!Rn9b"
        print(f"  Using hardcoded credentials: {login_username}")
        
        print()
        
        # Target profile and max posts - read from users.txt
        try:
            with open('users.txt', 'r') as f:
                content = f.read().strip()
                parts = content.split()
                
                if len(parts) >= 1:
                    profile_username = parts[0]
                    print(f"  Reading username from users.txt: {profile_username}")
                else:
                    print("  ❌ users.txt is empty!")
                    profile_username = input("Profile to scrape: ").strip()
                
                if len(parts) >= 2:
                    try:
                        max_posts = int(parts[1])
                        print(f"  Reading max posts from users.txt: {max_posts}")
                    except ValueError:
                        print(f"  ⚠️ Invalid max posts value '{parts[1]}', using all posts")
                        max_posts = None
                else:
                    print("  ⚠️ No max posts specified in users.txt, using all posts")
                    max_posts = None
                    
        except FileNotFoundError:
            print("  ❌ users.txt file not found!")
            profile_username = input("Profile to scrape: ").strip()
            max_posts = input("Max posts (or Enter for all): ").strip()
            max_posts = int(max_posts) if max_posts else None
        except Exception as e:
            print(f"  ❌ Error reading users.txt: {e}")
            profile_username = input("Profile to scrape: ").strip()
            max_posts = input("Max posts (or Enter for all): ").strip()
            max_posts = int(max_posts) if max_posts else None
        
        print("\n" + "="*60 + "\n")
        
        session_data, requests = await scraper.scrape_profile(
            profile_username=profile_username,
            max_posts=max_posts,
            login_username=login_username,
            login_password=login_password
        )
        
        if session_data:
            print("\n🔑 Session data:")
            print(json.dumps(session_data, indent=2))
    
    finally:
        logger.close()
        sys.stdout = sys.__stdout__
        print("\n✓ Log saved")


if __name__ == "__main__":
    asyncio.run(main())