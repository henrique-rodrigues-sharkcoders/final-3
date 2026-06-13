from playwright.sync_api import sync_playwright
import random


# ==========================================
# SCRAPER VINTED (STEALTH BASIC)
# ==========================================

def scrape_vinted(search="nike", max_items=30):

    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        page = browser.new_page()

        url = f"https://www.vinted.pt/vetement?search_text={search}&order=newest_first"

        page.goto(url, timeout=60000)
        page.wait_for_timeout(random.randint(4000, 7000))

        items = page.query_selector_all("[data-testid='item-box-container']")

        print(f"🔎 {search} -> {len(items)} items")

        for item in items[:max_items]:

            try:
                title = item.query_selector("h3").inner_text()
            except:
                title = "Unknown"

            try:
                price_text = item.query_selector("[data-testid='item-box-price']").inner_text()
                price = float(price_text.replace("€", "").replace(",", ".").strip())
            except:
                price = 0

            try:
                link = item.query_selector("a").get_attribute("href")
                url_item = "https://www.vinted.pt" + link
            except:
                url_item = ""

            brand = "Unknown"

            # estimativa simples (placeholder realista)
            estimated_value = price * 1.5 if price > 0 else 0

            profit = estimated_value - price
            roi = (profit / price) * 100 if price > 0 else 0

            score = (roi * 0.7) + (profit * 0.3)

            results.append((
                title,
                brand,
                price,
                url_item,
                estimated_value,
                profit,
                roi,
                score
            ))

        browser.close()

    return results