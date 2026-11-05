import requests
import time
import os
import sys
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

TARGET = os.getenv("TARGET", "https://968-store.com")
WORDLIST = os.getenv("WORDLIST", "wordlist.txt")
DELAY = float(os.getenv("DELAY", "0.3"))
TIMEOUT = int(os.getenv("TIMEOUT", "5"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

INTERESTING = {200, 201, 204, 301, 302, 307, 401, 403, 500}

GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"


def check(path):
    url = f"{TARGET}/{path.lstrip('/')}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT,
                         allow_redirects=False, verify=False)
        content_type = r.headers.get("Content-Type", "")
        content_length = len(r.content)

        if r.status_code == 200 and "text/html" in content_type and content_length > 800:
            return None
        return r.status_code
    except requests.exceptions.RequestException:
        return None


def main():
    try:
        with open(WORDLIST, "r", encoding="utf-8", errors="ignore") as f:
            words = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{RED}[!] File not found: {WORDLIST}{RESET}")
        sys.exit(1)

    print(f"[*] Target: {TARGET}")
    print(f"[*] Wordlist: {WORDLIST} ({len(words)} words)")
    print(f"[*] Delay: {DELAY}s\n")

    found = 0
    for i, word in enumerate(words, 1):
        if word.startswith("#"):
            continue

        status = check(word)
        if status is None:
            continue

        if status in INTERESTING:
            if status == 200:
                color = GREEN
            elif status in (301, 302, 307):
                color = CYAN
            elif status in (401, 403):
                color = YELLOW
            else:
                color = RED

            print(f"{color}[{status}] {TARGET}/{word}{RESET}", flush=True)
            found += 1

        time.sleep(DELAY)

        if i % 500 == 0:
            print(f"[*] Progress: {i}/{len(words)} - Found: {found}", flush=True)

    print(f"\n[*] Scan complete. Found {found} interesting paths.")


if __name__ == "__main__":
    main()
