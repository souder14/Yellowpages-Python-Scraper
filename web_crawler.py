# This script scrapes business information like phone numbers, emails, Instagram URLs
# etc. from Yellow Pages using Selenium. It gets URLs from an input CSV, launches
# Chrome in headless mode, visits each URL, extracts data, clicks "Visit Website" links
# to get additional info, and exports the results to a CSV file.

import csv
import re
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import os
import sys

# Function to scrape phone number, business name, email, and Instagram URL from a webpage
def scrape_page(driver):
    phone_number = driver.find_element(By.CLASS_NAME, 'phone.dockable').text.strip()
    name = driver.find_element(By.CLASS_NAME, 'dockable.business-name').text.strip()
    email = extract_emails(driver.page_source)
    instagram_url = extract_instagram_url(driver.page_source)

    return phone_number, name, email, instagram_url

# Function to extract email addresses from text
def extract_emails(text):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif']
    emails = re.findall(email_regex, text)
    filtered_emails = set(email for email in emails if not any(ext in email for ext in image_extensions))
    return filtered_emails

# Function to extract Instagram URL from text
def extract_instagram_url(text):
    instagram_regex = r'https?://(www\.)?instagram\.com/[A-Za-z0-9_]+/?'
    instagram_urls = re.findall(instagram_regex, text)
    return instagram_urls[0] if instagram_urls else ''

# Function to clean up the text before saving to the CSV file
def clean_text(text):
    cleaned_text = text.strip()
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Remove extra whitespaces
    return cleaned_text

# Function to get the website name from a URL
def get_website_name(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

# Path to the CSV file containing the URLs
csv_file = 'the_scraped_urls.csv'

# Get the path of the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Path to the Chrome web driver executable
driver_path = os.path.join(current_directory, 'chromedriver.exe')

# Initialize the Service object with the path to the ChromeDriver executable
service = Service(driver_path)

# Initialize the ChromeOptions object
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress log messages
chrome_options.add_argument('--headless')  # Run Chrome in headless mode

# Redirect error output to null device
sys.stderr = open(os.devnull, 'w')

# Initialize the web driver with ChromeOptions
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the business_info.csv file for writing
business_info_file = open(os.path.join(current_directory, 'business_info.csv'), 'w', newline='')
csv_writer = csv.writer(business_info_file)
csv_writer.writerow(['Combined Phone', 'Name', 'Email', 'Address', 'Instagram URL'])

# Read the URLs from the CSV file and visit each one
with open(os.path.join(current_directory, csv_file), 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row if present

    urls = list(reader)
    total_urls = len(urls)

    rows_to_write = []  # Accumulate rows to write in batches

    for i, row in enumerate(urls, 1):
        url = row[0]
        print(f'Crawling {url}...')

        driver.get(url)

        print(f'Processing URL {i}/{total_urls} - {url}')

        # Scrape phone number, business name, email, and Instagram URL
        try:
            phone, name, email, instagram_url = scrape_page(driver)
            phone = clean_text(phone)
            name = clean_text(name)
            email = [clean_text(e) for e in email]
            instagram_url = clean_text(instagram_url)
            rows_to_write.append([phone, name, ', '.join(email), get_website_name(url), instagram_url])
            print(f'Scraped phone: {phone}')
            print(f'Scraped name: {name}')
            print(f'Scraped email: {", ".join(email)}')
            print(f'Website: {get_website_name(url)}')
            print(f'Instagram URL: {instagram_url}')
        except Exception as e:
            print(f'Error scraping page: {e}')

        # Click the "Visit Website" link if present
        try:
            website_link = driver.find_element(By.CLASS_NAME, 'website-link.dockable')
            actions = ActionChains(driver)
            actions.move_to_element(website_link).perform()
            website_link.click()

            # Wait for the new page to load
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[1])  # Switch to the new window/tab

            # Scrape email addresses from the website
            try:
                email = extract_emails(driver.page_source)
                if email:
                    email = [clean_text(e) for e in email]
                    rows_to_write.append(['', '', ', '.join(email), get_website_name(driver.current_url), ''])
                    print(f'Scraped email (Website): {", ".join(email)}')
                    print(f'Website: {get_website_name(driver.current_url)}')
            except Exception as e:
                print(f'Error scraping email from website: {e}')

            # Scrape Instagram URL from the website
            try:
                instagram_url = extract_instagram_url(driver.page_source)
                if instagram_url and 'instagram.com' in instagram_url:
                    instagram_url = clean_text(instagram_url)
                    rows_to_write.append(['', '', '', '', instagram_url])
                    print(f'Instagram URL (Website): {instagram_url}')
            except Exception as e:
                print(f'Error scraping Instagram URL from website: {e}')

            driver.close()  # Close the new window/tab
            driver.switch_to.window(driver.window_handles[0])  # Switch back to the original window/tab
        except NoSuchElementException:
            print('No "Visit Website" link found.')

        print()  # Add a blank line for readability

        # Write rows in batches
        if len(rows_to_write) >= 100:
            csv_writer.writerows(rows_to_write)
            rows_to_write = []

    # Write any remaining rows
    if rows_to_write:
        csv_writer.writerows(rows_to_write)

# Close the business_info.csv file
business_info_file.close()

# Close the browser window
driver.quit()
