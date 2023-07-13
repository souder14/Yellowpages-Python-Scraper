# Yellowpages-Python-Scraper
A Python-based web scraping tool to extract contact information for local businesses from Yellowpages.com


I have developed a set of Python scripts that facilitate web scraping of contact information for local businesses from Yellowpages.com and business websites. The purpose of these scripts is to gather phone numbers, emails, addresses, and other relevant contact details for reaching out to businesses regarding an app that I am creating.

### Yellowpages Scraper:

This script focuses on scraping Yellowpages.com to locate and extract contact information for local businesses based on user-defined search terms. The script operates in the following manner:

Accepts user input for search terms.
Generates URLs for Yellowpages.com using the provided search terms and locations.
Eliminates duplicate URLs.
Sends requests to each URL to scrape the respective webpage.
Extracts business names, phone numbers, emails, addresses, and other relevant information from the page's HTML.
Saves the scraped contact information to a CSV file.
I developed this script because Yellowpages.com offers contact details for numerous local businesses, making it an ideal starting point for identifying potential businesses to approach.

### Business Website Crawler

This script focuses on crawling business websites to discover contact information such as emails and addresses. The script operates as follows:

Takes a CSV file containing business URLs obtained from the Yellowpages scraper.
Visits each business URL.
Clicks on the "Visit Website" link to access the respective business website.
Extracts emails from the HTML of each business website.
Saves the scraped emails and website URLs to a CSV file.
I developed this script as a complementary tool to the Yellowpages scraper, as the Yellowpages listings do not always include email addresses. The business website crawler enables me to retrieve direct business email addresses from their websites.

Highlighted Features of the Code:

>User Input: The Yellowpages scraper allows users to input search terms, enabling customized searches for specific types of local businesses.

>URL Generation: The script dynamically generates URLs for Yellowpages.com based on the user-provided search terms and locations. This ensures targeted scraping of relevant business listings.

>Duplicate URL Removal: The script includes a mechanism to eliminate duplicate URLs, preventing redundant scraping and data duplication.

>Web Page Scraping: The scripts utilize the BeautifulSoup library to scrape HTML content from web pages. This allows extraction of various contact information such as business names, phone numbers, emails, addresses, etc.

>CSV Data Storage: The scraped contact information is saved to CSV files, providing a structured format for easy access and analysis. Each script saves the relevant data to separate CSV files.

>Business Website Crawling: The business website crawler script leverages the Selenium library to crawl and interact with business websites. It simulates clicking on the "Visit Website" link to access the respective business sites for further data extraction.

The code is designed with modularity in mind, making it adaptable to scrape and extract data from other similar websites like Yelp, Google Maps, TripAdvisor, and more. With minor adjustments to the selectors and attributes, the core scraping, crawling, and data storage logic can be reused for different sites.

Prerequisites

To install the required packages, use the following command:

```
shell
pip install -r requirements.txt
```

Ensure that you have the chromedriver.exe file downloaded and placed in the same folder as the scripts. This driver is necessary for the proper functioning of the web scraping process.

With minor changes to the selectors and attributes, these scripts can likely be adapted to scrape and extract data from other similar sites such as Yelp, Google Maps, TripAdvisor, and more. The core logic for scraping, crawling, and storing data remains reusable.
