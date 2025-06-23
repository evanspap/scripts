#!/usr/bin/env python3

"""
Download all .sdf or .sdf.gz files from NCI DTP Compound Sets page (no Selenium needed).
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Constants
BASE_URL = "https://wiki.nci.nih.gov"
PAGE_URL = "https://wiki.nci.nih.gov/spaces/NCIDTPdata/pages/160989212/Compound+Sets"

# Usage header
header = """
Download .sdf or .sdf.gz files from the NCI DTP Compound Sets (no Selenium).
Usage:
    python download_nci_sdf_final.py [output_folder] [--dry-run]

Example:
    python download_nci_sdf_final.py ./nci_sdf --dry-run
"""

# Parse command line arguments
if len(sys.argv) < 2:
    print(header)
    sys.exit(1)

output_dir = sys.argv[1]
dry_run = "--dry-run" in sys.argv
os.makedirs(output_dir, exist_ok=True)

# Download and parse the page
print("Running: Downloading and parsing the Compound Sets page...")
response = requests.get(PAGE_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Extract valid .sdf or .sdf.gz links
links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if ".sdf" in href and "/download/attachments/" in href:
        full_url = urljoin(BASE_URL, href)
        links.append(full_url)

print(f"Found {len(links)} file(s).")

# Dry run
if dry_run:
    for link in links:
        print("  [Dry-run] Would download:", link)
    print("✅ Dry run complete.")
    sys.exit(0)

# Download each file
for url in links:
    filename = os.path.basename(urlparse(url).path)
    filepath = os.path.join(output_dir, filename)
    print(f"Running: Downloading {filename}...")
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"⚠️ Failed to download {url}: {e}")

print("✅ All files downloaded.")
