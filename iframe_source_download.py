import os
from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

log_lock = Lock()
BASE_URL = "https://retrobowl-25-unblocked.github.io"

def log(message):
    with log_lock:
        print(f"[{time.strftime('%H:%M:%S')}] {message}")

def get_iframe_sources(html_file):
    """Extract iframe sources ending with .embed from HTML file"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            iframes = soup.find_all('iframe')
            embed_srcs = []
            
            for iframe in iframes:
                src = iframe.get('src', '')
                if src.endswith('.embed'):
                    embed_srcs.append(src.strip('/'))
                    
            return embed_srcs
    except Exception as e:
        log(f"Error reading {html_file}: {e}")
        return []

def download_embed(url, output_dir):
    """Download embed content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
        }
        
        full_url = urljoin(BASE_URL, url)
        response = requests.get(full_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Create output filename from URL
        filename = url.replace('.embed', '.html')
        output_path = os.path.join(output_dir, filename)
        
        # Create subdirectories if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        log(f"Downloaded: {url}")
        return True
        
    except Exception as e:
        log(f"Error downloading {url}: {e}")
        return False

def main():
    # Configuration
    games_dir = './'
    output_dir = 'downloaded_embeds'
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all HTML files
    html_files = [os.path.join(games_dir, f) for f in os.listdir(games_dir) 
                 if f.endswith('.html')]
    log(f"Found {len(html_files)} HTML files")
    
    # Extract all embed sources
    all_sources = []
    for html_file in html_files:
        sources = get_iframe_sources(html_file)
        if sources:
            log(f"Found {len(sources)} embed sources in {html_file}")
            all_sources.extend(sources)
    
    # Remove duplicates
    unique_sources = list(set(all_sources))
    log(f"\nTotal unique embed sources found: {len(unique_sources)}")
    
    # Download embeds using thread pool
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Create download tasks
        futures = [executor.submit(download_embed, src, output_dir) 
                  for src in unique_sources]
        
        # Wait for all downloads to complete and count successes
        successful = sum(1 for future in futures if future.result())
    
    log(f"\nDownload complete!")
    log(f"Successfully downloaded: {successful}/{len(unique_sources)} embeds")

if __name__ == '__main__':
    main()