from vinted_scraper import VintedScraper

scraper = VintedScraper("https://www.vinted.com")
items = scraper.search({"search_text": "board games"})

for item in items:
    print(f"{item.title} - {item.price}")