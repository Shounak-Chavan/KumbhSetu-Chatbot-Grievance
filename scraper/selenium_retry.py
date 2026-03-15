"""
Selenium Retry — nashikkumbhmela.org/yatra-guide/
Saves to: ../dataset/kumbh_rag_dataset/spiritual/
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# CONFIG

url      = "https://nashikkumbhmela.org/yatra-guide/"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
save_dir = os.path.normpath(
    os.path.join(BASE_DIR, "..", "dataset", "kumbh_rag_dataset", "spiritual")
)
filename = os.path.join(save_dir, "doc_3.txt")

# CHROME SETUP

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

def main():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # SCRAPE WITH RETRY
    print(f"⏳ Fetching: {url}")

    text = None

    for attempt in range(3):
        try:
            driver.get(url)
            time.sleep(4)  # wait for JS to render

            text = driver.find_element("tag name", "body").text

            if text and len(text) > 200:
                print(f"✅ Got content — {len(text)} chars")
                break
            else:
                text = None
                print(f"⚠️  Attempt {attempt+1}: empty content, retrying...")
                time.sleep(3)

        except Exception as e:
            print(f"❌ Attempt {attempt+1} error: {e}")
            time.sleep(3)

    driver.quit()

    # SAVE
    if text:
        os.makedirs(save_dir, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"SOURCE: {url}\n\n")
            f.write(text)
        print(f"✅ Saved → {filename}")
    else:
        print("❌ Failed to extract content after 3 attempts")


if __name__ == "__main__":
    main()