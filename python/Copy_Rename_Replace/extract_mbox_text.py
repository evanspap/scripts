
#!/usr/bin/env python3
"""extract_mbox_text.py – Pulls plain text out of a Gmail‑style .mbox file with progress display."""

import argparse, csv, sys, mailbox, email
from email import policy
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

def html_to_text(html: str) -> str:
    if not BeautifulSoup:
        return html
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text(" ", strip=True)

def get_body(msg: email.message.EmailMessage) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp  = part.get_content_disposition()
            if disp == "attachment":
                continue
            payload = part.get_payload(decode=True)
            try:
                text = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
            except AttributeError:
                text = ""
            if ctype == "text/plain":
                return text
            if ctype == "text/html":
                return html_to_text(text)
    else:
        if msg.get_content_type() == "text/plain":
            return msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="replace")
        if msg.get_content_type() == "text/html":
            raw = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="replace")
            return html_to_text(raw)
    return ""

def print_progress(index, total):
    percent = (index + 1) * 100 // total
    print(f"Processing: {percent}% ({index + 1}/{total})", end="\r")

def main():
    ap = argparse.ArgumentParser(description="Extract readable text from an MBOX, skipping attachments.")
    ap.add_argument("mbox", help="Path to .mbox file exported from Google Takeout or similar")
    ap.add_argument("-o", "--output", default="emails.txt", help="File to write (default: emails.txt)")
    ap.add_argument("--csv", action="store_true", help="Write CSV with columns Date,From,Subject,Body instead of plain text.")
    args = ap.parse_args()

    mbox_path = Path(args.mbox).expanduser()
    box = mailbox.mbox(str(mbox_path), factory=lambda f: email.message_from_binary_file(f, policy=policy.default))
    total = len(box)

    if args.csv:
        out = open(args.output, "w", newline="", encoding="utf-8")
        writer = csv.writer(out)
        writer.writerow(["Date", "From", "Subject", "Body"])
        for i, msg in enumerate(box):
            writer.writerow([msg.get("Date", ""), msg.get("From", ""), msg.get("Subject", ""), get_body(msg)])
            print_progress(i, total)
        out.close()
    else:
        with open(args.output, "w", encoding="utf-8") as out:
            sep = "\n" + "-" * 80 + "\n"
            for i, msg in enumerate(box):
                body = get_body(msg)
                out.write(f"Email #{i+1}\nDate: {msg.get('Date','')}\nFrom: {msg.get('From','')}\nSubject: {msg.get('Subject','')}\n\n{body}{sep}")
                print_progress(i, total)
    print("\nDone. Wrote", args.output)

if __name__ == "__main__":
    main()
