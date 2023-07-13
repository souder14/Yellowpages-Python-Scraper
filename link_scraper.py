# This script scrapes business URLs from Yellow Pages using asyncio. It gets search
# terms and locations from the user, generates URLs, scrapes them asynchronously
# while handling failures, exports results to CSV, and tracks metrics.

import csv
import asyncio
import aiohttp
import time
from urllib.parse import urljoin, quote
from lxml import html
from concurrent.futures import ThreadPoolExecutor

# Async timeout
TIMEOUT = 30

# Rate limiting delay
REQUEST_DELAY = 1  

# Function to scrape URLs asynchronously
async def scrape_urls(urls):
    
    scraped_urls = set()

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch_url(session, url))
        
        scraped_urls_lists = await asyncio.gather(*tasks)

        for urls in scraped_urls_lists:
            scraped_urls.update(urls)

    return list(scraped_urls)

async def fetch_url(session, url):
    try:
        async with session.get(url, timeout=TIMEOUT) as response:
            await asyncio.sleep(REQUEST_DELAY)
            response.raise_for_status()
            tree = html.fromstring(await response.text())
            urls = tree.xpath("//a[@class='business-name']/@href")
            return [urljoin(url, u) for u in urls if '/mip/' in u]

    except Exception as e:
        print(f"Unable to scrape {url}. Error: {e}")
        return []
        
# Function to add custom locations
def add_custom_locations(locations_input):
    new_locations = [loc.strip() for loc in locations_input.split(",") if loc.strip()]
    location_terms_list.extend(new_locations)
    print("Custom locations added successfully.")
    
# Function to count scraped businesses   
def count_businesses(scraped_urls):
    return len(scraped_urls)

# Function to calculate time taken
def time_taken(start_time):
    end_time = time.time()
    duration = end_time - start_time
    print(f"Completed in {int(duration//60)} min {int(duration%60)} sec")

# Predefined locations  
location_terms_list = [
    "Bethesda, MD",
    "Washington, DC",
    "Arlington, VA",
    "Alexandria, VA",
    "Silver Spring, MD",
    "Rockville, MD",
    "Fairfax, VA",
    "Reston, VA",
    "Falls Church, VA",
    "Gaithersburg, MD",
    "McLean, VA",
    "College Park, MD",
    "Vienna, VA",
    "Bowie, MD",
    "Annandale, VA",
    "Chevy Chase, MD",
    "Tysons, VA",
    "Herndon, VA",
    "Columbia, MD",
    "Frederick, MD",
    "Laurel, MD",
    "Greenbelt, MD",
    "Manassas, VA",
    "Germantown, MD",
    "Stafford, VA",
    "Leesburg, VA",
    "Woodbridge, VA",
    "Annapolis, MD",
    "Hagerstown, MD",
    "Winchester, VA",
    "Fredericksburg, VA"
]

# Get user inputs
num_links = input("How many links to generate (0 for unlimited)? ")  
if num_links != '0':
    num_links = int(num_links)
    
search_terms = input("Enter search terms (comma separated): ").split(",")
search_terms = [term.strip() for term in search_terms]

# Generate urls
base_url = 'https://www.yellowpages.com/search?search_terms={}&geo_location_terms=' 

urls = []
for search_term in search_terms:
    for location in location_terms_list:
        urls.append(base_url.format(quote(search_term)) + quote(location.replace(" ", "+")))
        
# Add page variations        
additional_urls = [url + f'&page={i}' for url in urls for i in range(2, 8)]
urls.extend(additional_urls)

# Clean and remove duplicates from the URLs
urls = list(set(urls))

# Scrape urls
start_time = time.time()

async def main():
    total_urls = len(urls)
    completed_urls = 0
    print(f"Scraping {total_urls} URLs...")
    scraped_urls = await scrape_urls(urls)
    completed_urls = len(scraped_urls)
    print(f"Total businesses found: {count_businesses(scraped_urls)}")
    time_taken(start_time) 

    # Export scraped urls
    csv_file = "scraped_urls.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f) 
        writer.writerows([[url] for url in scraped_urls])

    print(f"Scraped urls exported to {csv_file}")

    if completed_urls < total_urls:
        print(f"Failed to scrape {total_urls - completed_urls} URLs.")

asyncio.run(main())
