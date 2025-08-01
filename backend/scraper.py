# blog/utils/scraper.py

import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- NEW: Centralized selectors for specific sites ---
SITE_SPECIFIC_SELECTORS = {
    'darkreading.com': 'div#article-main',
    # Add other site-specific selectors here as needed
    # 'bleepingcomputer.com': 'div.article-body', 
}

def initialize_chrome_driver():
    """Initializes a Selenium Chrome WebDriver for running in a server environment."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Failed to initialize Chrome WebDriver: {e}")
        return None

def scrape_article_content(url, chrome_driver=None, force_selenium_for_this_url=False, timeout=15, max_retries=3, delay_range=(1,3)):
    """Scrapes the main content of an article from a given URL."""
    domain = requests.utils.urlparse(url).netloc
    
    if force_selenium_for_this_url and chrome_driver:
        print(f"Using Selenium for {url}")
        try:
            chrome_driver.get(url)
            selector = SITE_SPECIFIC_SELECTORS.get(domain)
            
            if selector:
                # Wait for the specific content element to be present
                wait = WebDriverWait(chrome_driver, timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                content_element = chrome_driver.find_element(By.CSS_SELECTOR, selector)
                return content_element.get_attribute('innerText')
            else:
                 # If no specific selector, fall back to the whole body after load
                print(f"No specific selector for {domain}. Getting full page source via Selenium.")
                return chrome_driver.find_element(By.TAG_NAME, 'body').get_attribute('innerText')

        except Exception as e:
            print(f"Selenium scraping failed for {url}: {e}")
            return None # If Selenium fails, we don't fall back to requests

    # --- Standard requests-based scraping (for sites that don't need Selenium) ---
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                selector = SITE_SPECIFIC_SELECTORS.get(domain, 'article, .post-content, .entry-content, .article-body') # Default selectors
                
                content_area = soup.select_one(selector)
                if content_area:
                    return content_area.get_text(separator='\n', strip=True)
                else:
                    # Fallback if no specific selectors match
                    return soup.body.get_text(separator='\n', strip=True) if soup.body else None

            elif response.status_code == 403:
                print(f"Anti-bot measure detected (403) for URL: {url}")
                # This would be the place to trigger a Selenium retry if desired
                return None 

        except requests.RequestException as e:
            print(f"Request failed for {url} on attempt {attempt + 1}: {e}")
            time.sleep(delay_range[0])
            
    return None # Return None if all retries fail