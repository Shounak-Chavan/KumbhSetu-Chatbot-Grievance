import requests
import trafilatura
from tqdm import tqdm
import json
import pdfplumber
import os
import time

# Define the data sources for each category
data_sources = {
 
    """ Paste you links here"""
}

# Define headers to mimic a browser visit
HEADERS = {
    "User-Agent": 
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # chatbot/scraper/
base_folder = os.path.join(BASE_DIR, "..", "dataset", "kumbh_rag_dataset")
base_folder = os.path.normpath(base_folder)  # clean up the path

failed_urls = []

# Create base folder if it doesn't exist
os.makedirs(base_folder, exist_ok=True)
for category in data_sources.keys():
    os.makedirs(os.path.join(base_folder, category), exist_ok=True)
 
print(f"\n📁 Dataset will be saved to: {base_folder}\n")

# Scraper with retry

def scrape_page(url,retries=3):
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=25)
            response.raise_for_status()
            text = trafilatura.extract(
                response.text,
                include_tables=True,
                include_comments=False,
                include_links=False
                )
        
            if text and len(text) > 200:
                return text
            
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3)  # wait 3s before retrying
        
    return None
        
# Main scraping loop

total_success = 0
total_failed = 0

for category, urls in data_sources.items():

    for i, url in enumerate(tqdm(urls,desc=f"📂 {category}")):

        time.sleep(1)  # polite delay

        text = scrape_page(url)

        filename = os.path.join(
            base_folder,
            category,
            f"doc_{i+1}.txt"
        )

        if text:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"SOURCE: {url}\n\n")
                f.write(text)
            total_success += 1
        else:
            failed_urls.append(
                {"category": category, "url": url}
            )
 
            total_failed += 1
            print(f"\n  ⚠️  Failed: {url}")

# Save failed URLs for review

if failed_urls:
 
    with open(
        os.path.join(base_folder, "failed_urls.json"),
        "w"
    ) as f:
        json.dump(failed_urls, f, indent=2)
 
    print(f"\n  {total_failed} URLs failed — check failed_urls.json")
 
else:
 
    print("\n  All URLs scraped successfully!")

# Summary of results

print(f"\n  ✅ Total successful scrapes: {total_success}")
print(f"\n  ❌ Total failed scrapes: {total_failed}")
