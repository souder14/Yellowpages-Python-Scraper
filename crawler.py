import csv
import re
import time
import random
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

MAX_DEPTH = 3  # Maximum depth limit for crawling
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
]

def scrape_page(url):
    options = Options()
    options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
    service = Service('chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        phone_numbers = driver.find_elements(By.CLASS_NAME, 'phone.dockable')
        business_names = driver.find_elements(By.CLASS_NAME, 'dockable.business-name')

        phone_number = phone_numbers[0].text.strip() if phone_numbers else ''
        name = business_names[0].text.strip() if business_names else ''

        return phone_number, name

    except Exception as e:
        print(f'Error scraping page: {e}')
        return '', ''

    finally:
        driver.quit()

def get_urls(base_url, depth=1):
    urls = []

    options = Options()
    options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
    service = Service('chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(base_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'business-name')))

        business_names = driver.find_elements(By.CLASS_NAME, 'business-name')
        extracted_urls = [urljoin(base_url, a.get_attribute('href')) for a in business_names]

        urls.extend(extracted_urls)

        if depth < MAX_DEPTH:
            next_link = driver.find_element(By.CLASS_NAME, 'next')
            next_url = next_link.get_attribute('href')
            if next_url:
                urls.extend(get_urls(next_url, depth + 1))

    except Exception as e:
        print(f'Error getting URLs: {e}')

    finally:
        driver.quit()

    return urls

def scrape_urls(urls):
    scraped_data = []
    for url in tqdm(urls, desc='Scraping URLs'):
        phone_number, name = scrape_page(url)
        scraped_data.append((phone_number, name, url))
    return scraped_data

def remove_duplicates(data):
    seen = set()
    unique_data = []
    for item in data:
        if item[2] not in seen:
            seen.add(item[2])
            unique_data.append(item)
    return unique_data

def save_data_to_csv(data):
    timestamp = time.strftime('%Y%m%d%H%M%S')
    file_name = f'business_info_{timestamp}.csv'
    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Phone', 'Name', 'URL'])
        writer.writerows(data)
    print(f'Data saved to {file_name}')

if __name__ == '__main__':
    base_url = 'https://www.yellowpages.com/search?search_terms={}&geo_location_terms='

    search_terms_input = input("Enter the search terms (separated by commas): ")
    search_terms = [term.strip() for term in search_terms_input.split(",")]
    urls = [base_url.format(quote(term)) for term in search_terms]

    data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(get_urls, urls)
        for result in results:
            data.extend(result)

    unique_data = remove_duplicates(data)
    scraped_data = scrape_urls(unique_data)
    save_data_to_csv(scraped_data)
