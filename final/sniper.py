import time
import requests

from vinted_scraper import scrape_vinted
from config import DISCORD_WEBHOOK, SLEEP_TIME


# =========================================
# STATE (only new items tracking)
# =========================================

seen_urls = set()


# =========================================
# NORMALIZER (VERY IMPORTANT)
# =========================================

def normalize_url(url: str) -> str:
    return url.split("?")[0]


# =========================================
# DISCORD
# =========================================

def send_discord(item):

    title, brand, price, url, est, profit, roi, score = item

    payload = {
        "content": f"""🆕 NEW VINTED LISTING

📦 {title}
💰 €{price}
🔗 {url}
"""
    }

    r = requests.post(DISCORD_WEBHOOK, json=payload)

    print("Discord status:", r.status_code)


# =========================================
# PROCESS ITEMS
# =========================================

def process(items):

    new_count = 0

    for item in items:

        title, brand, price, url, est, profit, roi, score = item

        url = normalize_url(url)

        # ONLY NEW ITEMS
        if url in seen_urls:
            continue

        seen_urls.add(url)

        new_count += 1

        print("🆕 NEW:", title)

        send_discord(item)

    print(f"📊 New items this cycle: {new_count}")

    return new_count


# =========================================
# MAIN LOOP
# =========================================

def run():

    print("🚀 VINTED SNIPER STARTED (NEW ONLY MODE)")

    SEARCH_QUERIES = [
        "nike",
        "adidas",
        "jordan",
        "sneakers",
        "hoodie",
        "jacket",
        "vintage",
        "streetwear"
    ]

    while True:

        all_items = []

        print("\n==============================")
        print("🚀 SCANNING")
        print("==============================")

        for q in SEARCH_QUERIES:

            try:
                items = scrape_vinted(q)
                all_items.extend(items)

                time.sleep(1)

            except Exception as e:
                print("Scraper error:", e)

        process(all_items)

        print(f"⏳ Sleeping {SLEEP_TIME}s...\n")
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    run()