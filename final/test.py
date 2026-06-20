from vinted_scraper import scrape_vinted

items = scrape_vinted("nike", max_items=10)

print("\nTOTAL:", len(items))
print("-" * 50)

for item in items:

    title, brand, price, url, est, profit, roi, score = item

    print("TITLE :", title)
    print("PRICE :", price)
    print("URL   :", url)
    print("-" * 50)