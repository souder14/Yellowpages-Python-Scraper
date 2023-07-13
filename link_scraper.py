import csv
import sys
import time
from urllib.parse import urljoin, quote
import keyboard
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

session = requests.Session()

# Rate limiting settings
REQUEST_DELAY = 1  # Delay in seconds between requests

# Function to scrape URLs
def scrape_urls(urls):
    scraped_urls = []
    total_urls = len(urls)

    def scrape_url(url, index):
        # Send a GET request to the specified URL with rate limiting
        print(f"Scraping URL: {url}")
        retries = 3  # Maximum number of retries
        while retries > 0:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = session.get(url, headers=headers)
                response.raise_for_status()  # Raise an exception for non-200 status codes
                break
            except requests.exceptions.RequestException as e:
                print(f"Failed to scrape URL: {url}. Error: {e}")
                retries -= 1
                if retries == 0:
                    return
                print("Retrying...")
                time.sleep(REQUEST_DELAY)

        # Create a BeautifulSoup object from the response content
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Failed to parse HTML for URL: {url}. Error: {e}")
            return

        # Find all anchor tags with class name 'business-name'
        business_names = soup.find_all('a', class_='business-name')

        # Extract the URLs from the anchor tags and concatenate with the base URL
        extracted_urls = [urljoin(url, a['href']) for a in business_names if '/mip/' in a['href']]
        print(f"Extracted {len(extracted_urls)} URLs")
        scraped_urls.extend(extracted_urls)

        # Print progress update
        print(f"Scraped URLs from {index} out of {total_urls} URLs.")

    with ThreadPoolExecutor() as executor:
        # Submit URL scraping tasks to the executor
        futures = [executor.submit(scrape_url, url, i+1) for i, url in enumerate(urls)]

        # Wait for all tasks to complete
        for future in futures:
            future.result()

    return scraped_urls

def remove_duplicates(urls):
    return list(set(urls))

def calculate_possible_urls(search_terms_count, locations_count):
    return search_terms_count * locations_count

# Function to add custom locations to the location terms list
def add_custom_locations(locations_input):
    new_locations = [loc.strip() for loc in locations_input.split(",") if loc.strip()]
    location_terms_list.extend(new_locations)
    print("Custom locations added successfully.")

# Prompt the user to enter the search terms separated by commas
search_terms_input = input("Enter the search terms (separated by commas): (e.g., Hair Salon, Restaurant): ")
search_terms = [term.strip() for term in search_terms_input.split(",")]

# Replace the search term in the URL
base_url = 'https://www.yellowpages.com/search?search_terms={}&geo_location_terms='.format(quote(search_terms[0]))

# Predefined list of location terms around the DMV area
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

# Display the available location terms
print("Choose an option:")
print("1. Select all locations")
print("2. Select specific locations")
print("3. Add custom locations")

# Prompt the user to choose an option
try:
    option = int(input())
except ValueError:
    print("Invalid option!")
    sys.exit()

# Validate the option
if option < 1 or option > 3:
    print("Invalid option!")
    sys.exit()

# Create a list of modified URLs with the search terms and the encoded location terms
urls = []
if option == 1:
    # Select all locations for each search term
    urls = [base_url + quote(search_term) + quote(location_term.replace(" ", "+")) for search_term in search_terms for location_term in location_terms_list]
elif option == 2:
    # Select specific locations for each search term
    print("Choose the locations (separated by commas):")
    print("Available locations:")
    for i, location in enumerate(location_terms_list, start=1):
        print(f"{i}. {location}")
    selection_input = input("Enter the corresponding numbers: ")
    selected_locations = selection_input.split(",")
    for selected_location in selected_locations:
        try:
            index = int(selected_location.strip()) - 1
            if index >= 0 and index < len(location_terms_list):
                location = location_terms_list[index]
                urls.extend([base_url + quote(search_term) + quote(location.replace(" ", "+")) for search_term in search_terms])
            else:
                print("Invalid location selection!")
                sys.exit()
        except ValueError:
            print("Invalid location selection!")
            sys.exit()
elif option == 3:
    # Add custom locations
    custom_locations_input = input("Enter the custom locations (separated by commas): ")
    add_custom_locations(custom_locations_input)

# Get the count of search terms and selected locations
search_terms_count = len(search_terms)
locations_count = len(urls) // search_terms_count

# Calculate the number of possible URLs
possible_urls_count = calculate_possible_urls(search_terms_count, locations_count)

# Print the count of possible URLs
print(f"\nPossible URLs: {possible_urls_count}")

# Ask if the user wants to continue processing the URLs
proceed = input("Do you want to continue processing these URLs? (y/n): ")

# If the user does not want to proceed, exit the script
if proceed.lower() != 'y':
    print("Exiting the script.")
    sys.exit()

# Remove duplicate URLs
urls = remove_duplicates(urls)

# Scrape URLs from the modified URLs
try:
    scraped_urls = scrape_urls(urls)
except Exception as e:
    print(f"Error occurred while scraping URLs: {e}")
    sys.exit()

# Export the scraped URLs to a CSV file named "urls.csv"
csv_file_name = "urls.csv"
try:
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Scraped URLs"])
        writer.writerows([[url] for url in scraped_urls])
    print(f"\nPossible URLs: {possible_urls_count}")
    print(f"Scraped URLs exported to {csv_file_name}.")
except Exception as e:
    print(f"Failed to export scraped URLs to {csv_file_name}. Error: {e}")
