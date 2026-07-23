# app.py - Full Anti-Detection Bot (7 Layers)
# This bot uses mathematical brute-force to simulate human behavior
# and avoid Google's bot detection.

from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import requests
import random
import time
import math
import os
import re

app = Flask(__name__)

# =============================================
# LAYER 1: IP ROTATION + TESTING
# =============================================

PROXY_SOURCES = [
    "https://raw.githubusercontent.com/mohammedcha/ProxRipper/main/full_proxies/https.txt",
    "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repository/main/proxy_list.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies.txt"
]

def fetch_free_proxies():
    """Fetch proxies from multiple sources and return a list of working ones."""
    all_proxies = []
    for url in PROXY_SOURCES:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                proxies = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', response.text)
                all_proxies.extend(proxies)
        except:
            continue
    
    # Remove duplicates
    all_proxies = list(set(all_proxies))
    
    # Quick test (only keep those that respond within 2 seconds)
    working_proxies = []
    for proxy in all_proxies[:50]:  # Limit to 50 to save time
        if test_proxy(proxy):
            working_proxies.append(proxy)
    
    return working_proxies if working_proxies else ["127.0.0.1:8080"]

def test_proxy(proxy):
    """Test if a proxy responds quickly."""
    try:
        response = requests.get("http://httpbin.org/ip", 
                                proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                                timeout=2)
        return response.status_code == 200
    except:
        return False

# =============================================
# LAYER 2: BROWSER FINGERPRINT RANDOMIZATION
# =============================================

VIEWPORT_SIZES = [(1366, 768), (1440, 900), (1536, 864), (1920, 1080), (1280, 800)]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
]

TIMEZONES = [
    "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
    "Europe/London", "Europe/Paris", "Asia/Tokyo", "Asia/Shanghai", "Australia/Sydney"
]

LANGUAGES = [
    ["en-US", "en"],
    ["en-GB", "en"],
    ["en-CA", "en"],
    ["fr-FR", "fr"],
    ["de-DE", "de"],
    ["es-ES", "es"],
    ["ja-JP", "ja"],
    ["zh-CN", "zh"]
]

# =============================================
# LAYER 3: WEBDRIVER REMOVAL + CHROME SPOOFING
# =============================================

def get_stealth_script():
    """Returns JavaScript that removes webdriver and adds fake browser properties."""
    return """
    // Remove webdriver
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // Add chrome object
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };
    
    // Add plugins
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
            { name: 'Native Client', filename: 'internal-nacl-plugin' }
        ]
    });
    
    // Add languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en']
    });
    
    // Add platform
    Object.defineProperty(navigator, 'platform', {
        get: () => 'Win32'
    });
    
    // Add hardware concurrency
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => 8
    });
    
    // Add device memory
    Object.defineProperty(navigator, 'deviceMemory', {
        get: () => 8
    });
    
    // Override permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = function(parameters) {
        if (parameters.name === 'notifications') {
            return Promise.resolve({ state: Notification.permission });
        }
        return originalQuery(parameters);
    };
    """

# =============================================
# LAYER 4: HUMAN MOUSE MOVEMENT (Bezier + Jitter)
# =============================================

def human_mouse_move(page, target_x, target_y):
    """Move mouse in a curved path with micro-movements and overshoot."""
    start_x, start_y = 0, 0  # Starting point (current mouse position)
    
    # Add overshoot: move past the target and then come back
    overshoot = random.uniform(0.95, 1.05)
    target_x *= overshoot
    target_y *= overshoot
    
    # Bezier control points with random offset
    cp1_x = (start_x + target_x) / 2 + random.gauss(0, 60)
    cp1_y = (start_y + target_y) / 2 + random.gauss(0, 60)
    cp2_x = (start_x + target_x) / 2 + random.gauss(0, 60)
    cp2_y = (start_y + target_y) / 2 + random.gauss(0, 60)
    
    # Generate 60 points on the curve
    points = []
    for t in range(0, 61):
        t = t / 60
        # Cubic Bezier formula
        x = (1-t)**3 * start_x + 3*(1-t)**2*t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * target_x
        y = (1-t)**3 * start_y + 3*(1-t)**2*t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * target_y
        # Add micro-movements (±5 pixels)
        x += random.gauss(0, 3)
        y += random.gauss(0, 3)
        points.append((int(x), int(y)))
    
    # Move with random delays (accelerate, then decelerate)
    for i, (x, y) in enumerate(points):
        # Speed variation: fast at start, slow at end
        progress = i / len(points)
        if progress < 0.3:
            delay = random.uniform(0.02, 0.05)
        elif progress < 0.7:
            delay = random.uniform(0.05, 0.12)
        else:
            delay = random.uniform(0.08, 0.20)
        page.mouse.move(x, y)
        time.sleep(delay)

# =============================================
# LAYER 5: HUMAN TYPING (Variable Delays + Typos)
# =============================================

def human_typing(page, text):
    """Type with variable delays, thinking pauses, and occasional typos."""
    for i, char in enumerate(text):
        # 5% chance of making a typo
        if random.random() < 0.05 and char != ' ':
            # Type a wrong character
            wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
            page.keyboard.type(wrong_char)
            time.sleep(random.uniform(0.2, 0.5))
            page.keyboard.press('Backspace')
            time.sleep(random.uniform(0.1, 0.3))
        
        # Type the correct character
        page.keyboard.type(char)
        
        # Thinking pause (10% chance)
        if random.random() < 0.10:
            time.sleep(random.uniform(0.5, 1.5))
        else:
            # Variable delay: faster at beginning, slower at end
            progress = i / len(text)
            if progress < 0.3:
                delay = random.uniform(0.05, 0.1)
            elif progress < 0.7:
                delay = random.uniform(0.08, 0.18)
            else:
                delay = random.uniform(0.1, 0.25)
            time.sleep(delay)

# =============================================
# LAYER 6: HUMAN PAGE LOAD (Random Waits + Scrolling)
# =============================================

def human_wait(min_sec=2.0, max_sec=5.0):
    """Wait like a human (random time between min and max)."""
    time.sleep(random.uniform(min_sec, max_sec))

def human_scroll(page):
    """Scroll down slowly with random pauses."""
    for _ in range(random.randint(2, 5)):
        # Scroll down a random amount
        page.mouse.wheel(delta_y=random.randint(100, 400))
        human_wait(0.3, 1.0)
        if random.random() < 0.3:  # 30% chance to stop and "read"
            human_wait(0.5, 2.0)

# =============================================
# LAYER 7: BEHAVIORAL NOISE (Human Mistakes)
# =============================================

def human_mistakes(page):
    """Add random human-like mistakes (hover wrong element, etc.)."""
    # Random hover on a non-target element
    if random.random() < 0.15:
        try:
            page.hover('a')  # Hover on the first link
            human_wait(0.3, 0.8)
        except:
            pass
    
    # Random move mouse to empty area
    if random.random() < 0.1:
        page.mouse.move(random.randint(0, 500), random.randint(0, 500))
        human_wait(0.2, 0.6)

# =============================================
# MAIN SEARCH FUNCTION (All Layers Active)
# =============================================

def perform_search(keyword):
    """Execute a Google search with full human behavior simulation."""
    
    # LAYER 1: Get a working proxy
    proxies = fetch_free_proxies()
    if not proxies:
        return f"https://www.google.com/search?q={keyword}"
    
    proxy = random.choice(proxies)
    print(f"Using proxy: {proxy}")
    
    with sync_playwright() as p:
        try:
            # LAYER 2: Browser fingerprint randomization
            viewport = random.choice(VIEWPORT_SIZES)
            user_agent = random.choice(USER_AGENTS)
            timezone = random.choice(TIMEZONES)
            language = random.choice(LANGUAGES)
            
            # Launch browser with stealth args
            browser = p.chromium.launch(
                headless=True,  # Use headless for Cloud Run (can set to False for debugging)
                proxy={"server": f"http://{proxy}"},
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                    '--disable-features=BlockInsecurePrivateNetworkRequests',
                    '--disable-features=OutOfBlinkCors',
                    '--window-size={},{}'.format(viewport[0], viewport[1])
                ]
            )
            
            # Create context with randomized settings
            context = browser.new_context(
                viewport={'width': viewport[0], 'height': viewport[1]},
                user_agent=user_agent,
                timezone_id=timezone,
                locale=language[0],
                extra_http_headers={
                    'Accept-Language': language[0]
                }
            )
            
            page = context.new_page()
            
            # LAYER 3: Remove webdriver and add chrome spoofing
            page.add_init_script(get_stealth_script())
            
            # LAYER 6: Human page load (random wait)
            print("Loading Google...")
            page.goto("https://www.google.com", timeout=30000)
            human_wait(2.0, 5.0)
            
            # Type the search term (LAYER 5 + LAYER 7)
            print(f"Typing: {keyword}")
            page.click('textarea[name="q"]')
            human_wait(0.5, 1.0)  # Pause before typing
            human_typing(page, keyword)
            human_wait(0.3, 1.0)  # Pause before pressing Enter
            
            # Press Enter and wait for results (LAYER 6)
            page.keyboard.press("Enter")
            human_wait(2.0, 5.0)
            page.wait_for_load_state('domcontentloaded')
            page.wait_for_selector('h3', timeout=20000)
            
            # LAYER 7: Add some human mistakes before clicking
            human_mistakes(page)
            
            # LAYER 4: Human mouse movement to first result
            print("Moving to first result...")
            first_result = page.locator('h3').first
            box = first_result.bounding_box()
            if box:
                target_x = box['x'] + box['width'] / 2
                target_y = box['y'] + box['height'] / 2
                # Add random offset to simulate slight inaccuracy
                target_x += random.gauss(0, 10)
                target_y += random.gauss(0, 10)
                human_mouse_move(page, target_x, target_y)
            
            # Pause before clicking
            human_wait(0.5, 1.5)
            
            # Click the result
            print("Clicking first result...")
            first_result.click()
            
            # Wait for final page to load (LAYER 6)
            human_wait(2.0, 4.0)
            page.wait_for_load_state('domcontentloaded')
            
            # Get final URL
            final_url = page.url
            print(f"Final URL: {final_url}")
            
            browser.close()
            return final_url
            
        except Exception as e:
            print(f"Error: {e}")
            browser.close()
            return f"https://www.google.com/search?q={keyword}"

# =============================================
# FLASK API ENDPOINTS
# =============================================

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

@app.route('/click', methods=['POST'])
def handle_click():
    data = request.get_json()
    keyword = data.get('keyword', 'mediatakeout')
    user_id = data.get('userId', 'anonymous')
    
    print(f"Processing: '{keyword}' for user {user_id}")
    
    final_url = perform_search(keyword)
    
    return jsonify({
        "status": "success",
        "final_url": final_url
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
