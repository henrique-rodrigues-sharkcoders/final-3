from playwright.sync_api import sync_playwright
import re
import random


def scrape_vinted(search="nike", max_items=30):

    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = f"https://www.vinted.pt/catalog?search_text={search}"

        page.goto(url, timeout=60000)
        page.wait_for_timeout(random.randint(4000, 7000))

        items = page.locator("a[href*='/items/']")

        print(f"🔎 {search} -> {items.count()} links")

        for i in range(min(items.count(), max_items)):

            el = items.nth(i)

            try:
                href = el.get_attribute("href")

                if not href:
                    continue

                # FIX URL DUPLICADO
                url_item = href if href.startswith("http") else "https://www.vinted.pt" + href

                text = el.inner_text().strip()

                # limpa texto
                lines = [x.strip() for x in text.split("\n") if x.strip()]

                title = lines[0] if len(lines) > 0 else "Unknown"

                # extrair preço corretamente
                price = 0
                for l in lines:
                    match = re.search(r"(\d+[,.]?\d*)\s?€", l)
                    if match:
                        price = float(match.group(1).replace(",", "."))

                est = price * 1.5 if price > 0 else 0
                profit = est - price
                roi = (profit / price) * 100 if price > 0 else 0
                score = roi * 0.7 + profit * 0.3

                results.append((
                    title,
                    "unknown",
                    price,
                    url_item,
                    est,
                    profit,
                    roi,
                    score
                ))

            except:
                continue

        browser.close()

    return results