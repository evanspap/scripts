#!/usr/bin/env python3

"""
Final working version (no Selenium) to download .sdf/.sdf.gz files from the NCI DTP Compound Sets wiki page.

Usage:
    python download_nci_sdf_final.py [output_folder] [--dry-run]
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

header = """
Download all .sdf/.sdf.gz files from the NCI DTP Compound Sets (no Selenium).
Usage:
    python download_nci_sdf_final.py [output_folder] [--dry-run]

Example:
    python download_nci_sdf_final.py ./nci_sdf --dry-run
"""

BASE_URL = "https://wiki.nci.nih.gov"
REAL_PAGE = "https://wiki.nci.nih.gov/spaces/NCIDTPdata/pages/viewpage.action?pageId=160989212"

if len(sys.argv) < 2:
    print(header)
    sys.exit(1)

output_dir = sys.argv[1]
dry_run = "--dry-run" in sys.argv

os.makedirs(output_dir, exist_ok=True)

print("Running: Downloading and parsing the actual Compound Sets page...")
resp = requests.get(REAL_PAGE)
soup = BeautifulSoup(resp.text, 'html.parser')

links = []
for a in soup.find_all("a", href=True):
    href = a['href']
    if href.endswith(".sdf") or href.endswith(".sdf.gz"):
        full_url = urljoin(BASE_URL, href)
        links.append(full_url)

print(f"Found {len(links)} file(s).")

if dry_run:
    for link in links:
        print("  [Dry-run] Would download:", link)
    print("✅ Dry run complete.")
    sys.exit(0)

for link in links:
    filename = os.path.basename(link.split('?')[0])
    filepath = os.path.join(output_dir, filename)
    print(f"Running: Downloading {filename}...")
    r = requests.get(link, stream=True)
    with open(filepath, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

print("✅ All files downloaded.")
