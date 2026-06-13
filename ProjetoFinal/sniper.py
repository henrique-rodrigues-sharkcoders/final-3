import time
import requests

from vinted_scraper import scrape_vinted
from db import init_db, save
from config import DISCORD_WEBHOOK


# ==========================================
# CONFIG
# ==========================================

SEARCH_QUERIES = [
    "nike",
    "adidas",
    "jordan",
    "sneakers",
    "hoodie",
    "jacket",
    "streetwear",
    "vintage",
    "bag",
    "pants"
]

MIN_ROI = 15
MIN_PROFIT = 5
SLEEP_TIME = 30

seen_urls = set()


# ==========================================
# DISCORD ALERT
# ==========================================

def send_discord_alert(item):

    title, brand, price, url, est, profit, roi, score = item

    payload = {
        "content": "🔥 **VINTED SNIPER ALERT**",
        "embeds": [
            {
                "title": title,
                "url": url,
                "color": 5763719,
                "fields": [
                    {"name": "💰 Price", "value": f"€{price}", "inline": True},
                    {"name": "📈 Profit", "value": f"€{profit:.2f}", "inline": True},
                    {"name": "🚀 ROI", "value": f"{roi:.2f}%", "inline": True},
                    {"name": "📊 Score", "value": f"{score:.2f}", "inline": True},
                ]
            }
        ]
    }

    try:
        r = requests.post(DISCORD_WEBHOOK, json=payload)

        if r.status_code == 204:
            print("📩 Discord alert sent")
        else:
            print("❌ Discord error:", r.status_code, r.text)

    except Exception as e:
        print("❌ Webhook error:", e)


# ==========================================
# DETECTION ENGINE
# ==========================================

def detect_bargains(listings):

    alerts = []

    for item in listings:

        title, brand, price, url, est, profit, roi, score = item

        if price <= 0:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        print(f"DEBUG -> {title} | €{price} | ROI {roi:.1f}%")

        if roi >= MIN_ROI and profit >= MIN_PROFIT:

            print("\n🔥 BARGAIN FOUND")
            print(title)

            send_discord_alert(item)
            alerts.append(item)

    return alerts


# ==========================================
# SNIPER LOOP
# ==========================================

def run_sniper():

    print("🚀 INIT VINTED SNIPER")
    init_db()

    while True:

        print("\n==============================")
        print("🚀 SCANNING MARKET")
        print("==============================")

        all_listings = []

        for q in SEARCH_QUERIES:

            try:
                print(f"🔎 Searching: {q}")

                listings = scrape_vinted(q)

                if listings:
                    all_listings.extend(listings)

                time.sleep(1.5)

            except Exception as e:
                print("Scraper error:", e)

        if all_listings:

            save(all_listings)

            alerts = detect_bargains(all_listings)

            print(f"\n📊 Total listings: {len(all_listings)}")
            print(f"🔥 Alerts sent: {len(alerts)}")

        else:
            print("❌ No listings found")

        print(f"\n⏳ Sleeping {SLEEP_TIME}s...\n")
        time.sleep(SLEEP_TIME)


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    run_sniper()