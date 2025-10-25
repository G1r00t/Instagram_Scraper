from patchright.sync_api import sync_playwright
import json
import time
import os
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_automation.log'),
        logging.StreamHandler()
    ]
)

class InstagramAutomation:
    def __init__(self, config=None):
        """Initialize the Instagram automation with configuration"""
        self.config = {
            'request_delay': 3,  # Seconds between profile visits
            'headless': False,  # Set to True to hide browser
            'max_retries': 3,  # Max retry attempts for failures
            'timeout': 30000,  # Page timeout in milliseconds
        }
        if config:
            self.config.update(config)
        
        # Data storage
        self.all_cookies = {}
        self.all_headers = {}
        self.network_requests = []
        self.user_ids = {}
        self.errors = []
        
        # Output directory
        self.output_dir = 'instagram_data_output'
        os.makedirs(self.output_dir, exist_ok=True)
        
        logging.info("Instagram Automation initialized")
        logging.info(f"Configuration: {json.dumps(self.config, indent=2)}")
    
    def read_profiles(self, filename='profiles.txt'):
        """Read Instagram usernames from file"""
        try:
            if not os.path.exists(filename):
                logging.error(f"File {filename} not found!")
                logging.info("Creating sample profiles.txt file...")
                with open(filename, 'w') as f:
                    f.write("# Add Instagram usernames here (one per line)\n")
                    f.write("# Example:\n")
                    f.write("# instagram\n")
                return []
            
            with open(filename, 'r') as f:
                profiles = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            logging.info(f"Loaded {len(profiles)} profiles from {filename}")
            return profiles
        except Exception as e:
            logging.error(f"Error reading profiles: {str(e)}")
            return []
    
    def extract_cookies(self, context, profile):
        """Extract all cookies from browser context"""
        try:
            cookies = context.cookies()
            cookie_dict = {}
            
            important_cookies = [
                'csrftoken', 'sessionid', 'datr', 'ig_did', 
                'mid', 'ds_user_id', 'ig_nrcb', 'wd'
            ]
            
            for cookie in cookies:
                cookie_dict[cookie['name']] = {
                    'value': cookie['value'],
                    'domain': cookie['domain'],
                    'path': cookie['path'],
                    'secure': cookie.get('secure', False),
                    'httpOnly': cookie.get('httpOnly', False)
                }
            
            # Log important cookies found
            found_important = [c for c in important_cookies if c in cookie_dict]
            logging.info(f"[{profile}] Found {len(found_important)} important cookies: {', '.join(found_important)}")
            
            self.all_cookies[profile] = cookie_dict
            return cookie_dict
        except Exception as e:
            logging.error(f"[{profile}] Error extracting cookies: {str(e)}")
            self.errors.append(f"{profile}: Cookie extraction failed - {str(e)}")
            return {}
    
    def handle_network_request(self, request):
        """Handle intercepted network requests"""
        try:
            url = request.url
            
            # Only process Instagram API requests
            if 'instagram.com' not in url:
                return
            
            # Extract headers
            headers = dict(request.headers)
            
            # Check for GraphQL requests to extract user_id
            if 'graphql/query' in url:
                logging.info(f"📡 Captured GraphQL request: {url[:100]}...")
                
                # Parse URL for parameters
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                
                # Extract user_id from GraphQL variables
                if 'variables' in query_params:
                    try:
                        import urllib.parse
                        variables_str = urllib.parse.unquote(query_params['variables'][0])
                        variables = json.loads(variables_str)
                        
                        if 'id' in variables:
                            user_id = variables['id']
                            logging.info(f"🆔 Found user_id from GraphQL: {user_id}")
                        
                        if 'username' in variables:
                            username = variables['username']
                            logging.info(f"👤 Found username from GraphQL: {username}")
                            
                    except Exception as e:
                        logging.debug(f"Could not parse GraphQL variables: {e}")
                
                # Store network request data
                request_data = {
                    'timestamp': datetime.now().isoformat(),
                    'url': url,
                    'method': request.method,
                    'headers': headers,
                    'resource_type': request.resource_type,
                    'query_params': query_params
                }
                self.network_requests.append(request_data)
        
        except Exception as e:
            logging.error(f"Error handling network request: {str(e)}")
    
    def handle_network_response(self, response):
        """Handle network responses to extract additional data"""
        try:
            url = response.url
            
            # Check for GraphQL responses
            if 'graphql/query' in url:
                try:
                    if response.status == 200:
                        logging.info(f"✅ GraphQL Response Status: {response.status} for {url[:80]}...")
                except Exception as e:
                    pass  # Some responses can't be read
        
        except Exception as e:
            logging.error(f"Error handling network response: {str(e)}")
    
    def trigger_initial_load(self, page, profile):
        """Trigger initial page load to capture tokens and user data"""
        try:
            logging.info(f"[{profile}] Triggering initial page load...")
            
            # Small scroll to trigger any lazy loading
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(2)
            
            # Wait for any API calls to complete
            time.sleep(3)
            
            logging.info(f"[{profile}] Initial load completed")
            
        except Exception as e:
            logging.error(f"[{profile}] Error during initial load: {str(e)}")
            self.errors.append(f"{profile}: Initial load failed - {str(e)}")
    
    def extract_user_id(self, page, profile):
        """Extract user ID from page source or meta tags"""
        try:
            # Method 1: Check page source for user ID
            content = page.content()
            user_id_match = re.search(r'"profilePage_(\d+)"', content)
            if user_id_match:
                user_id = user_id_match.group(1)
                self.user_ids[profile] = user_id
                logging.info(f"[{profile}] Extracted user_id: {user_id}")
                return user_id
            
            # Method 2: Check meta tags
            user_id = page.evaluate("""
                () => {
                    const meta = document.querySelector('meta[property="al:ios:url"]');
                    if (meta) {
                        const match = meta.content.match(/instagram:\\/\\/user\\?username=(\\d+)/);
                        return match ? match[1] : null;
                    }
                    return null;
                }
            """)
            
            if user_id:
                self.user_ids[profile] = user_id
                logging.info(f"[{profile}] Extracted user_id from meta: {user_id}")
                return user_id
            
        except Exception as e:
            logging.error(f"[{profile}] Error extracting user_id: {str(e)}")
        
        return None
    
    def process_profile(self, page, context, profile):
        """Process a single Instagram profile"""
        try:
            logging.info(f"\n{'='*60}")
            logging.info(f"Processing profile: {profile}")
            logging.info(f"{'='*60}")
            
            # Navigate to profile
            url = f"https://www.instagram.com/{profile}/"
            logging.info(f"Navigating to: {url}")
            
            response = page.goto(url, wait_until='networkidle', timeout=self.config['timeout'])
            
            if not response or response.status != 200:
                logging.error(f"[{profile}] Failed to load profile (Status: {response.status if response else 'None'})")
                self.errors.append(f"{profile}: Failed to load profile")
                return False
            
            logging.info(f"[{profile}] Profile loaded successfully")
            
            # Wait for page to fully load
            time.sleep(3)
            
            # Extract cookies
            self.extract_cookies(context, profile)
            
            # Extract headers from page
            headers = page.evaluate("""
                () => {
                    const performance = window.performance.getEntries();
                    return {
                        userAgent: navigator.userAgent,
                        language: navigator.language,
                        platform: navigator.platform
                    }
                }
            """)
            self.all_headers[profile] = headers
            
            # Extract user ID
            self.extract_user_id(page, profile)
            
            # Trigger initial load to capture tokens
            self.trigger_initial_load(page, profile)
            
            # Wait a bit for any final requests
            time.sleep(2)
            
            logging.info(f"[{profile}] ✅ Profile processing completed")
            return True
            
        except Exception as e:
            logging.error(f"[{profile}] Error processing profile: {str(e)}")
            self.errors.append(f"{profile}: Processing failed - {str(e)}")
            return False
    
    def save_data(self):
        """Save all extracted data to files"""
        try:
            logging.info("\n" + "="*60)
            logging.info("Saving extracted data...")
            logging.info("="*60)
            
            # Save cookies
            cookies_file = os.path.join(self.output_dir, 'cookies.json')
            with open(cookies_file, 'w') as f:
                json.dump(self.all_cookies, f, indent=2)
            logging.info(f"✅ Saved cookies to: {cookies_file}")
            
            # Save headers
            headers_file = os.path.join(self.output_dir, 'headers.json')
            with open(headers_file, 'w') as f:
                json.dump(self.all_headers, f, indent=2)
            logging.info(f"✅ Saved headers to: {headers_file}")
            
            # Save network requests
            requests_file = os.path.join(self.output_dir, 'network_requests.json')
            with open(requests_file, 'w') as f:
                json.dump(self.network_requests, f, indent=2)
            logging.info(f"✅ Saved {len(self.network_requests)} network requests to: {requests_file}")
            
            
            # Save user_ids
            user_ids_file = os.path.join(self.output_dir, 'user_ids.txt')
            with open(user_ids_file, 'w') as f:
                for profile, user_id in self.user_ids.items():
                    f.write(f"{profile}: {user_id}\n")
            logging.info(f"✅ Saved user_ids to: {user_ids_file}")
            
            # Save combined data
            combined_data = {
                'extraction_time': datetime.now().isoformat(),
                'profiles_processed': list(self.all_cookies.keys()),
                'total_cookies': {profile: len(cookies) for profile, cookies in self.all_cookies.items()},
                'total_network_requests': len(self.network_requests),
                'user_ids': self.user_ids,
                'errors': self.errors,
                'config': self.config
            }
            
            combined_file = os.path.join(self.output_dir, 'instagram_data.json')
            with open(combined_file, 'w') as f:
                json.dump(combined_data, f, indent=2)
            logging.info(f"✅ Saved combined data to: {combined_file}")
            
            # Save errors if any
            if self.errors:
                errors_file = os.path.join(self.output_dir, 'errors.txt')
                with open(errors_file, 'w') as f:
                    for error in self.errors:
                        f.write(f"{error}\n")
                logging.warning(f"⚠️ Saved {len(self.errors)} errors to: {errors_file}")
            
            logging.info(f"\n✅ All data saved to directory: {self.output_dir}")
            
        except Exception as e:
            logging.error(f"Error saving data: {str(e)}")
    
    def print_summary(self):
        """Print summary of extraction"""
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"Profiles processed: {len(self.all_cookies)}")
        print(f"Total cookies extracted: {sum(len(c) for c in self.all_cookies.values())}")
        print(f"Total network requests captured: {len(self.network_requests)}")
        print(f"User IDs extracted: {len(self.user_ids)}")
        print(f"Errors encountered: {len(self.errors)}")
        print("="*60 + "\n")
    
    def run(self):
        """Main execution function"""
        try:
            logging.info("🚀 Starting Instagram Automation with Patchright")
            
            # Read profiles
            profiles = self.read_profiles()
            if not profiles:
                logging.error("No profiles to process. Exiting.")
                return
            
            # Start patchright
            with sync_playwright() as p:
                logging.info("Launching browser...")
                
                # Launch browser with stealth settings
                browser = p.chromium.launch(
                    headless=self.config['headless'],
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                
                # Create context with realistic settings
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                # Create page
                page = context.new_page()
                
                # Set up network monitoring
                page.on('request', self.handle_network_request)
                page.on('response', self.handle_network_response)
                
                logging.info("✅ Browser launched successfully")
                
                # Process each profile
                for idx, profile in enumerate(profiles, 1):
                    logging.info(f"\n[{idx}/{len(profiles)}] Processing: {profile}")
                    
                    success = self.process_profile(page, context, profile)
                    
                    if success:
                        logging.info(f"[{profile}] ✅ Successfully processed")
                    else:
                        logging.warning(f"[{profile}] ⚠️ Processing completed with errors")
                    
                    # Delay between profiles to avoid rate limiting
                    if idx < len(profiles):
                        delay = self.config['request_delay']
                        logging.info(f"Waiting {delay} seconds before next profile...")
                        time.sleep(delay)
                
                # Close browser
                logging.info("\nClosing browser...")
                browser.close()
            
            # Save all data
            self.save_data()
            
            # Print summary
            self.print_summary()
            
            logging.info("🎉 Instagram Automation completed successfully!")
            
        except Exception as e:
            logging.error(f"Fatal error in main execution: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())


def main():
    """Entry point for the script"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     Instagram Profile Scraper with Patchright             ║
    ║                                                            ║
    ║  ⚠️  IMPORTANT DISCLAIMER:                                 ║
    ║  This script is for educational purposes only.            ║
    ║  Scraping Instagram may violate their Terms of Service.   ║
    ║  Use responsibly and ethically.                           ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Configuration (customize as needed)
    config = {
        'request_delay': 3,     # Seconds between profile visits
        'headless': False,      # Set to True to hide browser
        'max_retries': 3,       # Max retry attempts
        'timeout': 30000,       # Page timeout in ms
    }
    
    # Create and run automation
    automation = InstagramAutomation(config)
    automation.run()


if __name__ == "__main__":
    main()