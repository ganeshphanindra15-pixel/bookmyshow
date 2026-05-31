"""
BookMyShow Ticket Availability Monitor
Checks if "Book Tickets" button is visible on the movie page.
"""

import os
import requests
import schedule
import time
import logging
import random
from datetime import datetime

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
BOT_TOKEN  = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
CHAT_ID    = os.environ.get("CHAT_ID", "YOUR_TELEGRAM_CHAT_ID")

CHECK_INTERVAL_MINUTES = int(os.environ.get("CHECK_INTERVAL_MINUTES", "30"))
# ──────────────────────────────────────────────────────────────────────────────

MOVIE_URL  = "https://in.bookmyshow.com/movies/hyderabad/veerabhadrudu/ET00455003"
MOVIE_NAME = "Veerabhadrudu"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger(__name__)

_last_notified_available = None

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://in.bookmyshow.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

def fetch_page():
    session = requests.Session()

    # Step 1: visit homepage to get cookies
    try:
        log.info("Warming up session...")
        session.get(
            "https://in.bookmyshow.com/",
            headers=get_headers(),
            timeout=15,
        )
        time.sleep(random.uniform(2.0, 4.0))
    except Exception as e:
        log.warning("Warmup failed: " + str(e))

    # Step 2: fetch the movie page
    try:
        log.info("Fetching movie page...")
        r = session.get(MOVIE_URL, headers=get_headers(), timeout=20)
        log.info("Status: " + str(r.status_code) + " | Length: " + str(len(r.text)))
        if r.status_code == 200:
            return r.text
        else:
            log.warning("Bad status: " + str(r.status_code))
            log.info("Preview: " + r.text[:300])
    except Exception as e:
        log.error("Fetch failed: " + str(e))

    return None

def is_booking_available(html):
    if not html:
        return False, "unknown"

    text_lower = html.lower()

    # Strong positive signal
    if "book tickets" in text_lower:
        return True, "found 'book tickets'"

    # Negative signals
    if "coming soon" in text_lower:
        return False, "coming soon"
    if "notify me" in text_lower:
        return False, "notify me (not open yet)"
    if "releasing on" in text_lower:
        return False, "releasing on (future date)"

    return False, "no booking signals found"

def send_telegram(message):
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    try:
        r = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": True,
        }, timeout=10)
        r.raise_for_status()
        log.info("Telegram notification sent.")
    except Exception as e:
        log.error("Telegram error: " + str(e))

def check_booking_availability():
    global _last_notified_available

    log.info("Checking ticket availability for " + MOVIE_NAME + "...")
    html = fetch_page()

    if html is None:
        log.warning("Could not fetch page, will retry next interval.")
        return

    available, reason = is_booking_available(html)
    log.info("Booking available: " + str(available) + " | Reason: " + reason)

    if available and _last_notified_available is not True:
        msg = (
            "BOOK TICKETS IS NOW AVAILABLE!\n\n"
            + MOVIE_NAME + " - Hyderabad\n"
            "Book now: " + MOVIE_URL + "\n\n"
            "Checked at: " + datetime.now().strftime("%d %b %Y %I:%M %p")
        )
        send_telegram(msg)
        _last_notified_available = True

    elif not available and _last_notified_available is True:
        send_telegram(MOVIE_NAME + " tickets no longer available.\nWill notify when they are back!")
        _last_notified_available = False
    else:
        log.info("No state change, skipping notification.")

def main():
    log.info("==================================================")
    log.info("BookMyShow Monitor started")
    log.info("Movie: " + MOVIE_NAME)
    log.info("Region: Hyderabad")
    log.info("Interval: every " + str(CHECK_INTERVAL_MINUTES) + " minutes")
    log.info("==================================================")

    check_booking_availability()
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_booking_availability)

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
