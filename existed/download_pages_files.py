import os
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

log_lock = Lock()

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with log_lock:
        print(f"[{timestamp}] [{level}] {message}")

def get_hrefs(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        return [a.get('href').replace('.html', '') 
                for a in soup.find_all('a') if a.get('href')]

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--no-sandbox')
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/120.0',
    ]
    chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
    
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    return webdriver.Chrome(options=chrome_options)

def handle_alert(driver):
    try:
        alert = driver.switch_to.alert
        alert.accept()
    except:
        pass

def save_html(args):
    url, existing_files, current_number, total_urls = args
    filename = f"{url}.html"
    
    if filename in existing_files:
        log(f"[{current_number}/{total_urls}] Skip: {filename}", "SKIP")
        return "skipped"
    
    for attempt in range(2):
        try:
            driver = setup_driver()
            full_url = f'https://retrobowl-25-unblocked.github.io/{url}'
            
            log(f"[{current_number}/{total_urls}] Get: {url} ({attempt + 1}/2)")
            driver.get(full_url)
            
            time.sleep(2)
            handle_alert(driver)
            
            html_content = driver.page_source
            with open(f'downloaded_pages/{filename}', 'w', encoding='utf-8') as f:
                f.write(html_content)
            log(f"[{current_number}/{total_urls}] OK: {filename}", "SUCCESS")
            return "success"
                
        except Exception as e:
            log(f"[{current_number}/{total_urls}] Err: {url} - {str(e)}", "ERROR")
            if attempt < 1:
                time.sleep(3)
        finally:
            if 'driver' in locals():
                try:
                    driver.quit()
                except:
                    pass
    return "failed"

def main():
    log("=== Start Download ===")
    
    os.makedirs('downloaded_pages', exist_ok=True)
    
    existing_files = set(os.listdir('existed'))
    log(f"Found {len(existing_files)} existing files")
    
    html_files = [os.path.join('pages', f) for f in os.listdir('pages') if f.endswith('.html')]
    urls = list(set(sum([get_hrefs(f) for f in html_files], [])))
    log(f"Found {len(urls)} URLs")
    
    args_list = [(url, existing_files, i+1, len(urls)) 
                 for i, url in enumerate(urls)]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(save_html, args_list))
    
    # Tính thống kê đúng cách
    success = results.count("success")
    skipped = results.count("skipped")
    failed = results.count("failed")
    
    log("=== Complete ===")
    log(f"Total: {len(urls)} | OK: {success} | Skip: {skipped} | Err: {failed}")

if __name__ == '__main__':
    main()