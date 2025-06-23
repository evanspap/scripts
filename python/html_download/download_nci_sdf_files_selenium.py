#!/usr/bin/env python3

"""
Download .sdf/.sdf.gz files from NCI DTP Compound Sets using Selenium (iframe-aware).

Usage:
    python download_nci_sdf_files_selenium.py [output_folder] [--dry-run]

Example:
    python download_nci_sdf_files_selenium.py ./nci_sdf --dry-run
"""

import os
import sys
import time
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

header = """
Download .sdf/.sdf.gz files from NCI DTP Compound Sets using Selenium.
Handles iframe content. Use --dry-run to list links only.
Usage:
    python download_nci_sdf_files_selenium.py [output_folder] [--dry-run]

Example:
    python download_nci_sdf_files_selenium.py ./nci_sdf --dry-run
"""

# Main page (with iframe inside)
URL = "https://wiki.nci.nih.gov/spaces/NCIDTPdata/pages/viewpage.action?pageId=160989212"

# --- Parse command-line args ---
if len(sys.argv) < 2:
    print(header)
    sys.exit(1)

output_dir = sys.argv[1]
dry_run = "--dry-run" in sys.argv
os.makedirs(output_dir, exist_ok=True)

# --- Setup headless Chrome ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

print("Running: Launching headless browser and accessing main page...")
driver.get(URL)
time.sleep(10)  # Allow time for iframe to load

# --- Switch to iframe ---
iframes = driver.find_elements("tag name", "iframe")
if not iframes:
    print("⚠️ No iframe found on the page.")
    driver.quit()
    sys.exit(1)

print("Running: Switching to iframe content...")
driver.switch_to.frame(iframes[0])
time.sleep(3)  # Let iframe fully render

# --- Search for .sdf or .sdf.gz links inside the iframe ---
elements = driver.find_elements("css selector", "a[href*='.sdf']")
links = []
for el in elements:
    href = el.get_attribute("href")
    if href and (".sdf" in href):
        links.append(href)

print(f"Found {len(links)} file(s).")

# --- Dry run: list links and exit ---
if dry_run:
    for link in links:
        print("  [Dry-run] Would download:", link)
    print("✅ Dry run complete.")
    driver.quit()
    sys.exit(0)

# --- Download files ---
for url in links:
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    out_path = os.path.join(output_dir, filename)
    print(f"Running: Downloading {filename}...")

    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"⚠️ Failed to download {url}: {e}")

driver.quit()
print("✅ All files downloaded.")
