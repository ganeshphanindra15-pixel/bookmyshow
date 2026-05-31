"""
BookMyShow Ticket Availability Monitor
Monitors ET00455003 (Veerabhadrudu) in Hyderabad and notifies via Telegram.
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

EVENT_CODE             = "ET00455003"
REGION_CODE            = "HYD"
CHECK_INTERVAL_MINUTES = int(os.environ.get("CHECK_INTERVAL_MINUTES", "30"))
# ──────────────────────────────────────────────────────────────────────────────

MOVIE_URL = "https://in.bookmyshow.com/movies/hyderabad/veerabhadrudu/ET00455003"
BMS_API   = "https://in.bookmyshow.com/api/movies-data/showtimes-by-event"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger(__name__)

_last_notified_available = None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer": "https://in.bookmyshow.com/",
    "Origin": "https://in.bookmyshow.com",
    "x-region-code": REGION_CODE,
    "x-region-slug": "hyderabad",
    "x-subregion-code": "",
    "appCode": "MOBAND2",
    "appVersion": "14.3.4",
    "platform": "AND",
}

def fetch_availability():
    """Check BookMyShow API for show availability."""
    session = requests.Session()

    # Warm up with homepage visit
    try:
        log.info("Warming up session...")
        session.get(
            "https://in.bookmyshow.com/",
            headers={
                "User-Agent": HEADERS["User-Agent"],
                "Accept": "text/html",
                "Accept-Language": "en-IN",
            },
            timeout=15,
        )
        time.sleep(random.uniform(1.5, 3.0))
    except Exception as e:
        log.warning("Warmup failed: " + str(e))

    # Try multiple BMS API endpoints
    endpoints = [
        "https://in.bookmyshow.com/api/movies-data/showtimes-by-event?appCode=MOBAND2&appVersion=14.3.4&language=en&eventCode=" + EVENT_CODE + "&regionCode=" + REGION_CODE + "&subRegionCode=&bmsId=1.21.0&token=67x1xa33&lat=17.3850&lon=78.4867",
        "https://in.bookmyshow.com/api/v2/movies/" + EVENT_CODE + "/showtimes?region=" + REGION_CODE,
        "https://in.bookmyshow.com/serv/getData?cmd=GETDATES&type=MT&code=" + EVENT_CODE + "&region=" + REGION_CODE,
    ]

    for url in endpoints:
        try:
            log.info("Trying: " + url[:80] + "...")
            r = session.get(url, headers=HEADERS, timeout=20)
            log.info("Status: " + str(r.status_code) + " | Length: " + str(len(r.text)))
            log.info("Preview: " + r.text[:300])

            if r.status_code == 200 and len(r.text) > 50:
                return r.text, r.status_code
        except Exception as e:
            log.warning("Failed: " + str(e))

    return None, None


def is_booking_available(response_text):
    """Check if booking is open based on response content."""
    if not response_text:
        return False

    text_lower = response_text.lower()

    # Positive signals — booking is open
    positive = [
        "showtime", "cinemas", "venue", "screen",
        "booktype", "sessionid", "shows", "theatres"
    ]

    # Negative signals — not yet open
    negative = [
        "no shows", "not available", "coming soon",
        "notify me", "no showtimes", "currently unavailable"
    ]

    for word in negative:
        if word in text_lower:
            log.info("Negative signal found: " + word)
            return False

    for word in positive:
        if word in text_lower:
            log.info("Positive signal found: " + word)
            return True

    return False


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

    log.info("Checking BookMyShow ticket availability for Veerabhadrudu in Hyderabad...")
    response_text, status = fetch_availability()

    if response_text is None:
        log.warning("Could not fetch data, will retry next interval.")
        return

    available = is_booking_available(response_text)
    log.info("Booking available: " + str(available))

    if available and _last_notified_available is not True:
        msg = (
            "TICKETS ARE NOW AVAILABLE!\n\n"
            "Veerabhadrudu - Hyderabad\n"
            "Book now: " + MOVIE_URL + "\n\n"
            "Checked at: " + datetime.now().strftime("%d %b %Y %I:%M %p")
        )
        log.info("Sending message: " + msg)
        send_telegram(msg)
        _last_notified_available = True

    elif not available and _last_notified_available is True:
        send_telegram("Veerabhadrudu tickets no longer available in Hyderabad.\nWill notify when they are back!")
        _last_notified_available = False
    else:
        log.info("No state change, skipping notification.")


def main():
    log.info("==================================================")
    log.info("BookMyShow Monitor started")
    log.info("Movie: Veerabhadrudu")
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
