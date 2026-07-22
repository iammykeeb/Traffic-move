# app.py - The Mathematical Brute-Force Bot
# All human behaviors are coded using math and randomization

from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import requests
import random
import time
import math
import os

app = Flask(__name__)

# =============================================
# 1. FETCH FREE PROXIES (Residential ISP look)
# =============================================
def fetch_free_proxies():
    """Scrape free residential proxies from GitHub"""
    try:
        response = requests.get(
            "https://raw.githubusercontent.com/mohammedcha/ProxRipper/main/full_proxies/https.txt",
            timeout=10
        )
        proxies = [p.strip() for p in response.text.splitlines() if p.strip()]
        return proxies
    except:
        return ["127.0.0.1:8080"]  # Fallback

# =============================================
# 2. HUMAN MOUSE MOVEMENT (Bezier Curve + Jitter)
# =============================================
def human_mouse_move(page, target_x, target_y):
    """Move mouse in a curved path with micro-movements"""
    start_x, start_y = 0, 0
    
    # Bezier control points with random offset
    cp1_x = (start_x + target_x) / 2 + random.gauss(0, 50)
    cp1_y = (start_y + target_y) / 2 + random.gauss(0, 50)
    cp2_x = (start_x + target_x) / 2 + random.gauss(0, 50)
    cp2_y = (start_y + target_y) / 2 + random.gauss(0, 50)
    
    # Generate 50 points on the curve
    points = []
    for t in range(0, 51):
        t = t / 50
        x = (1-t)**3 * start_x + 3*(1-t)**2*t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * target_x
        y = (1-t)**3 * start_y + 3*(1-t)**2*t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * target_y
        # Add micro-movements (±5 pixels) - Canvas fingerprint variation
        x += random.gauss(0, 2)
        y += random.gauss(0, 2)
        points.append((int(x), int(y)))
    
    # Move with random delays (50-100ms between points)
    for x, y in points:
        page.mouse.move(x, y)
        time.sleep(random.uniform(0.05, 0.1))

# =============================================
# 3. HUMAN TYPING (Variable Delays)
# =============================================
def human_typing(page, text):
    """Type with variable delays between keystrokes"""
    for char in text:
        page.keyboard.type(char)
        if random.random() < 0.1:  # 10% chance of a thinking pause
            time.sleep(random.uniform(0.5, 1.5))
        else:
            time.sleep(random.expovariate(0.01))  # Average 100ms delay

# =============================================
# 4. MAIN SEARCH FUNCTION (All human behaviors)
# =============================================
def perform_search(keyword):
    """Execute Google search with full human behavior simulation"""
    
    # Get a free proxy
    proxies = fetch_free_proxies()
    if not proxies:
        return "https://www.google.com"
    
    proxy = random.choice(proxies)
    print(f"Using proxy: {proxy}")
    
    with sync_playwright() as p:
        try:
            # Launch browser with stealth settings
            browser = p.chromium.launch(
                headless=False,  # Visible browser (more human-like)
                proxy={"server": f"http://{proxy}"},
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-web-security'
                ]
            )
            
            # Create context with realistic viewport
            context = browser.new_context(
                viewport={
                    'width': random.choice([1366, 1440, 1536, 1920]), 
                    'height': 768
                },
                user_agent=random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ])
            )
            
            page = context.new_page()
            
            # REMOVE navigator.webdriver (set to undefined)
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Add fake plugins to look more human
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Add fake languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
            
            # HUMAN PAGE LOAD: 2-5 seconds
            print("Loading Google...")
            page.goto("https://www.google.com", timeout=20000)
            time.sleep(random.uniform(2.0, 5.0))
            
            # HUMAN TYPING: Variable delays
            print(f"Typing: {keyword}")
            page.click('textarea[name="q"]')
            human_typing(page, keyword)
            
            # HUMAN PAUSE before pressing Enter
            time.sleep(random.uniform(0.3, 1.0))
            page.keyboard.press("Enter")
            
            # HUMAN PAGE LOAD: Wait 2-5 seconds
            print("Waiting for results...")
            time.sleep(random.uniform(2.0, 5.0))
            page.wait_for_load_state('domcontentloaded')
            page.wait_for_selector('h3', timeout=15000)
            
            # HUMAN MOUSE MOVEMENT: Bezier curve + jitter
            print("Moving to first result...")
            first_result = page.locator('h3').first
            box = first_result.bounding_box()
            if box:
                target_x = box['x'] + box['width'] / 2
                target_y = box['y'] + box['height'] / 2
                human_mouse_move(page, target_x, target_y)
            
            # HUMAN PAUSE before clicking
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click the result
            print("Clicking first result...")
            first_result.click()
            
            # HUMAN PAGE LOAD: Wait 2-4 seconds
            time.sleep(random.uniform(2.0, 4.0))
            page.wait_for_load_state('domcontentloaded')
            
            # Get the final URL
            final_url = page.url
            print(f"Final URL: {final_url}")
            
            browser.close()
            return final_url
            
        except Exception as e:
            print(f"Error: {e}")
            browser.close()
            return f"https://www.google.com/search?q={keyword}"

# =============================================
# 5. FLASK API ENDPOINTS
# =============================================
@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/click', methods=['POST'])
def handle_click():
    data = request.get_json()
    keyword = data.get('keyword', 'mediatakeout')
    user_id = data.get('userId', 'anonymous')
    
    print(f"Processing: {keyword} for user {user_id}")
    
    # Execute the search with full human behavior
    final_url = perform_search(keyword)
    
    return jsonify({
        "status": "success",
        "final_url": final_url
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
