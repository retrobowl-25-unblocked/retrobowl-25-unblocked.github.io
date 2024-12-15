import os
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
import time

def get_embed_urls(html_file):
    """Get .embed URLs from HTML file"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            urls = []
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src', '')
                if src.endswith('.embed'):
                    urls.append(src.strip('/'))
            return urls
    except Exception as e:
        print(f"Error reading {html_file}: {e}")
        return []

def download_embed_file(url):
    """Download .embed file"""
    try:
        response = requests.get(f'https://retrobowl-25-unblocked.github.io/{url}')
        filename = f"embed_files/{url}"
        
        # Create directories if needed
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Save the .embed file
        with open(filename, 'wb') as f:
            f.write(response.content)
            
        print(f"Downloaded: {url}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def main():
    os.makedirs('embed_files', exist_ok=True)
    
    # Get all HTML files in game directory
    html_files = [os.path.join('game', f) for f in os.listdir('game') 
                 if f.endswith('.html')]
                 
    # Get all .embed URLs
    all_urls = []
    for html_file in html_files:
        urls = get_embed_urls(html_file)
        all_urls.extend(urls)
    
    # Remove duplicates
    unique_urls = list(set(all_urls))
    print(f"Found {len(unique_urls)} .embed files to download")
    
    # Download files
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(download_embed_file, unique_urls))
    
    # Print results
    success = sum(results)
    print(f"\nDownload complete!")
    print(f"Successfully downloaded: {success}/{len(unique_urls)} files")

if __name__ == '__main__':
    main()