import queue
import threading
import time
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

# 1. Create a FIFO Queue and populate target URLs
url_queue = queue.Queue()

targets = [
    {
        "site": "Webscraper.io",
        "url": "https://webscraper.io/test-sites/e-commerce/allinone",
    },
    {
        "site": "Books_to_Scrape",
        "url": "https://books.toscrape.com/",
    },
    {
        "site": "Scrape_this_site",
        "url": "https://scrapethissite.com/pages/simple/",
    },
]

for target in targets:
    url_queue.put(target)


def parse_and_read_data(site_name, html_bytes):
    """Parses targeted data elements based on the specific site structure."""
    html_text = html_bytes.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html_text, "html.parser")

    print(f"\n=======================================================")
    print(f" Scraping Results for: {site_name}")
    print(f"=======================================================")

    # Targeted extraction for Books to Scrape
    if site_name == "Books_to_Scrape":
        books = soup.select(".product_pod")
        print(f"Found {len(books)} books. First 8 items:\n")
        for book in books[:8]:
            title = book.h3.a["title"]
            price = book.select_one(".price_color").text.strip()
            print(f"  • Title: {title}\n    Price: {price}\n")

    # Targeted extraction for Scrape This Site
    elif site_name == "Scrape_this_site":
        countries = soup.select(".country")
        print(f"Found {len(countries)} countries. First 30 items:\n")
        for country in countries[:30]:
            name = country.select_one(".country-name").text.strip()
            capital = country.select_one(".country-capital").text.strip()
            print(f"  • Country: {name} | Capital: {capital}")

    # Targeted extraction for Webscraper.io
    elif site_name == "Webscraper.io":
        items = soup.select(".thumbnail")
        print(f"Found {len(items)} products. First 8 items:\n")
        for item in items[:8]:
            title = item.select_one("a.title").text.strip()
            price = item.select_one(".price").text.strip()
            print(f"  • Product: {title} | Price: {price}")

def worker(thread_id):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }

    while True:
        try:
            target = url_queue.get(block=False)
        except queue.Empty:
            break

        site_name = target["site"]
        target_url = target["url"]

        try:
            req = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                html_data = response.read()
                # Run the parser function on fetched data
                parse_and_read_data(site_name, html_data)

        except Exception as e:
            print(f"\n============================================================")
            print(f"[Thread-{thread_id}] ERROR fetching {site_name}: {e}")         
            print("============================================================")

        finally:
            url_queue.task_done()

# 2. Spawn worker threads
NUM_THREADS = 3
threads = []

for i in range(1, NUM_THREADS + 1):
    t = threading.Thread(target=worker, args=(i,))
    t.start()
    threads.append(t)

# 3. Block main thread until all queue items are processed
url_queue.join()

# 4. Wait for all threads to exit safely
for t in threads:
    t.join()

print(f"\n=======================================================")
print(f"All scraping tasks completed successfully.")
print("=======================================================")
