# blog/utils/scraper.py

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import random
import logging

logger = logging.getLogger(__name__) # Use logging for better output control

# --- Configuration ---
CHROMEDRIVER_PATH = 'C:/Users/Chase/Documents/Pulses/drivers/chromedriver.exe'

# Rotate User-Agents to avoid detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36",
]

# Define a set of common selectors for main article content (for general fallback)
GENERAL_CONTENT_SELECTORS = [
    'div.article-body',
    'div.body-content',
    'div.article-content',
    'div.entry-content',
    'div.td-post-content',
    'main.content',
    'article',
    '.post-content',
    'div[itemprop="articleBody"]',
    'div[class*="content"]',
    'div[id*="content"]',
    'body',
]


def get_random_user_agent():
    return random.choice(USER_AGENTS)

def initialize_chrome_driver():
    """Initializes a Selenium Chrome WebDriver for running in a server environment."""
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # MUST run without a GUI in a server
    chrome_options.add_argument("--no-sandbox")  # Required for running as root in Docker/Linux
    chrome_options.add_argument("--disable-dev-shm-usage") # Overcomes limited resource problems

    try:
        # When browser-actions/setup-chrome is used, the driver is automatically in the system's PATH
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Failed to initialize Chrome WebDriver: {e}")
        return None

def scrape_article_content(url, chrome_driver=None, force_selenium_for_this_url=False, timeout=20, max_retries=3, delay_range=(1, 5)):
    """
    Attempts to scrape the main article content from the given URL.
    Returns a tuple: (scraped_text, requests_failed_anti_bot_like_error).
    requests_failed_anti_bot_like_error is True if requests failed due to 403/429.
    """
    scraped_content = None
    requests_failed_anti_bot_like_error = False

    if force_selenium_for_this_url and chrome_driver:
        logger.info(f"Forcing Selenium for {url} based on prior failures or configuration.")
        scraped_content = _scrape_with_selenium(chrome_driver, url, timeout)
    else:
        # Attempt scraping with requests first
        scraped_content, requests_failed_anti_bot_like_error = _scrape_with_requests(url, timeout, max_retries, delay_range)

        # If requests failed and Selenium is available, try Selenium as fallback
        if not scraped_content and chrome_driver:
            logger.info(f"Requests failed for {url}. Attempting with Selenium as fallback...")
            scraped_content = _scrape_with_selenium(chrome_driver, url, timeout)

    return scraped_content, requests_failed_anti_bot_like_error

def _scrape_with_requests(url, timeout=20, max_retries=3, delay_range=(1, 5)):
    """Enhanced scraping with better anti-bot detection handling, retries, and encoding.
       Returns (content, requests_failed_anti_bot_like_error)"""

    session = requests.Session()
    requests_failed_anti_bot_like_error = False

    for attempt in range(max_retries):
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        session.headers.update(headers)

        try:
            logger.info(f"Attempting requests.get for {url} (Attempt {attempt + 1}/{max_retries})")
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(delay_range[0], delay_range[1]))
            
            with session.get(url, timeout=timeout, stream=True) as response:
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                
                # Try to infer encoding from headers, default to utf-8
                encoding = response.encoding if response.encoding else 'utf-8'
                
                # Read content in chunks and decode, replacing problematic chars
                content_chunks = []
                for chunk in response.iter_content(chunk_size=8192):
                    content_chunks.append(chunk)
                raw_html = b''.join(content_chunks).decode(encoding, errors='replace')

            soup = None
            parsers = ['lxml', 'html.parser', 'html5lib'] # lxml first, then fallbacks
            
            for parser in parsers:
                try:
                    soup = BeautifulSoup(raw_html, parser)
                    if soup.find('body'): # Check if soup object seems valid
                        break
                    else:
                        logger.warning(f"Parser '{parser}' resulted in an empty body for {url}")
                        soup = None # Reset soup if body is empty
                except Exception as e:
                    logger.warning(f"Parser '{parser}' failed for {url}: {e}")
            
            if not soup:
                logger.error(f"All parsers failed to produce a valid soup object for {url}")
                raise ValueError("Failed to parse HTML") # Re-raise to trigger retry

            # Site-specific extraction logic
            domain = urlparse(url).netloc.lower()
            
            if 'thehackernews.com' in domain:
                content = _extract_hackernews_content(soup)
            elif 'cio.com' in domain:
                content = _extract_cio_content(soup)
            elif 'csoonline.com' in domain:
                content = _extract_csoonline_content(soup)
            elif 'securityweek.com' in domain:
                content = _extract_securityweek_content(soup)
            elif 'krebsonsecurity.com' in domain:
                content = _extract_krebs_content(soup)
            else:
                # Fallback to enhanced general extraction
                content = _extract_general_content(soup)
            
            if content and len(content.strip()) > 100: # Ensure substantial content was found
                return content, False # Success, not an anti-bot error
            else:
                logger.warning(f"Extracted content was too short or empty for {url} via requests. (Length: {len(content.strip()) if content else 0})")
                return None, False # Content not good enough, but not necessarily anti-bot

        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [403, 429]:
                logger.error(f"Anti-bot measure detected ({e.response.status_code}) for URL: {url}")
                requests_failed_anti_bot_like_error = True # Flag this specific type of error
            else:
                logger.error(f"HTTP {e.response.status_code} for URL: {url}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during requests scraping {url}: {e}")
            
        except ValueError as e: # Catch ValueError from failed parsing too
            logger.error(f"Parsing error during requests scraping {url}: {e}")

        except Exception as e:
            logger.error(f"An unexpected error occurred during requests scraping {url}: {e}")
            
        if attempt < max_retries - 1:
            # Exponential backoff with jitter
            sleep_time = (2 ** attempt) + random.uniform(0, 1)
            logger.info(f"Retrying {url} in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        else:
            logger.error(f"Failed to scrape content from {url} after {max_retries} requests attempts.")
            return None, requests_failed_anti_bot_like_error # Final failure, return anti-bot flag

    return None, requests_failed_anti_bot_like_error # Should not be reached if retries are handled by exceptions


# --- Site-Specific Extraction Functions (unchanged from previous version) ---
def _extract_hackernews_content(soup):
    """Extract content from TheHackerNews articles."""
    article_body_div = soup.select_one('div.articlebody.clear.cf')
    if article_body_div:
        content_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'li']
        extracted_paragraphs = []
        for element in article_body_div.find_all(content_tags):
            text = element.get_text(separator=' ', strip=True)
            if text:
                extracted_paragraphs.append(text)
        full_text = '\n\n'.join(extracted_paragraphs)
        return _clean_text(full_text)
    return _extract_general_content(soup)

def _extract_cio_content(soup):
    """Extract content from CIO.com articles."""
    selectors = [
        'div.content-body',
        'div.article-content',
        'div.post-content',
        'div[data-module="ArticleBody"]',
        'div.body-copy',
        'section.article-body',
        'div.entry-content',
        'article .content'
    ]
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            unwanted_selectors = [
                'script', 'style', 'nav', 'footer', 'header', 'aside', 'form',
                'img', 'figure', 'figcaption', '.social-share', '.ad', '.comments',
                '.related-articles', '.newsletter-signup', '.author-info', '.tags',
                '.category-links', '.timestamp', '.byline', 'blockquote.twitter-tweet'
            ]
            for unwanted in element.select(unwanted_selectors):
                unwanted.decompose()
            text = element.get_text(separator='\n', strip=True)
            if len(text) > 500:
                return _clean_text(text)
    return _extract_general_content(soup)

def _extract_csoonline_content(soup):
    """Extract content from CSO Online articles."""
    selectors = [
        'div[data-module="ArticleBody"]',
        'div.article-body',
        'div.content-body',
        'section.article-content',
        'div.post-body'
    ]
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            unwanted_selectors = [
                'script', 'style', '.social-share', '.ad', '.newsletter', '.related',
                '.author-info', '.tags', '.category-links', '.timestamp', '.byline'
            ]
            for unwanted in element.select(unwanted_selectors):
                unwanted.decompose()
            text = element.get_text(separator='\n', strip=True)
            if len(text) > 500:
                return _clean_text(text)
    return _extract_general_content(soup)

def _extract_securityweek_content(soup):
    """Extract content from SecurityWeek articles."""
    selectors = [
        'div.body-text',
        'div.article-body',
        'div.post-content',
        'section.content'
    ]
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            unwanted_selectors = [
                'script', 'style', '.social', '.ad', '.comments', '.tags', '.byline'
            ]
            for unwanted in element.select(unwanted_selectors):
                unwanted.decompose()
            text = element.get_text(separator='\n', strip=True)
            if len(text) > 500:
                return _clean_text(text)
    return _extract_general_content(soup)

def _extract_krebs_content(soup):
    """Extract content from KrebsOnSecurity articles."""
    selectors = [
        'div.entry-content',
        'div.post-content',
        'article .content'
    ]
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            unwanted_selectors = [
                'script', 'style', '.social', '.ad', '.comments', '.jp-relatedposts',
                '.sharedaddy', '.sd-social-icon', '.wpcnt'
            ]
            for unwanted in element.select(unwanted_selectors):
                unwanted.decompose()
            text = element.get_text(separator='\n', strip=True)
            if len(text) > 500:
                return _clean_text(text)
    return _extract_general_content(soup)

def _extract_general_content(soup):
    """Enhanced general content extraction with more comprehensive selectors and cleaning."""
    for selector in GENERAL_CONTENT_SELECTORS:
        element = soup.select_one(selector)
        if element:
            unwanted_selectors = [
                'script', 'style', 'nav', 'footer', 'header', 'aside', 'form',
                'img', 'figure', 'figcaption', 'svg', 'iframe', 'embed', 'object',
                '.social-share', '.social', '.ad', '.ads', '.advertisement',
                '.comments', '.comment', '.related', '.sidebar', '.widget',
                '.newsletter', '.signup', '.subscribe', '.promo', '.promotion',
                '.breadcrumb', '.navigation', '.nav', '.menu', '.share',
                '[class*="ad"]', '[id*="ad"]', '.dropcap',
                '.meta', '.post-meta', '.article-meta',
                '.author-box', '.tags-list', '.category-list',
                '.entry-header', '.post-header',
                '.jp-relatedposts', '.sharedaddy', '.sd-social-icon',
                'a[href*="mailto:"]', 'a[href*="tel:"]'
            ]
            for unwanted_selector in unwanted_selectors:
                for unwanted in element.select(unwanted_selector):
                    unwanted.decompose()
            text = element.get_text(separator='\n', strip=True)
            if len(text) > 300:
                lines = text.split('\n')
                filtered_lines = []
                for line in lines:
                    line = line.strip()
                    if (len(line) > 50 or
                        (len(line) > 10 and line.count(' ') > 2 and not re.search(r'^\W*(\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}-\d{2}-\d{2})\W*$', line, re.IGNORECASE))
                        and not re.match(r'^(Home|News|About|Contact|Share|Subscribe|Follow|Tags?|Categories)', line, re.I)
                        and not re.match(r'^\d+\s+(comments?|shares?|likes?)', line, re.I)
                        and not re.match(r'^(January|February|March|April|May|June|July|August|September|October|November|December)', line)):
                        filtered_lines.append(line)
                cleaned_text = '\n'.join(filtered_lines)
                return _clean_text(cleaned_text) if cleaned_text and len(cleaned_text.strip()) > 200 else None
    paragraphs = soup.find_all('p')
    if paragraphs:
        full_text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
        if len(full_text) > 300:
            return _clean_text(full_text)
    return None

def _clean_text(text):
    """Clean and normalize extracted text."""
    if not text:
        return None
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n(Share|Tweet|Pin|Like|Follow|Subscribe|View Comments|Print Article|Email Article|Topics|Related Content).*?\n', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'\n.*?(cookie|privacy policy|terms of service|copyright|all rights reserved|powered by).*?\n', '\n', text, flags=re.IGNORECASE)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if len(line) > 20 or (len(line) > 5 and line.count(' ') > 0 and not re.match(r'^[\d\s\W]*$', line)):
            cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)
    return text.strip()

def _scrape_with_selenium(driver, url, timeout=30):
    """Performs Selenium scraping using an already initialized WebDriver instance."""
    try:
        logger.info(f"Attempting Selenium for {url}")
        driver.get(url)

        wait = WebDriverWait(driver, timeout)
        content_selectors = [
            'div[data-module="ArticleBody"]',
            'div.article-content',
            'div.post-content',
            'div.entry-content',
            'article',
            'div.body-text',
            'div.main-content',
            'section.article-body',
            'div.content-body',
            'div.article-body'
        ]
        
        content_element = None
        for selector in content_selectors:
            try:
                content_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                logger.info(f"Selenium found content element with selector: {selector}")
                break
            except TimeoutException:
                continue
            except NoSuchElementException:
                logger.warning(f"Selenium could not find element with selector: {selector} using visibility check.")
                try:
                    content_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if content_element.is_displayed():
                        logger.info(f"Selenium found element with selector: {selector} (is displayed).")
                        break
                except NoSuchElementException:
                    continue
        
        if not content_element:
            logger.warning(f"No specific content selector found for {url} after waiting. Proceeding with full page source.")

        # Give a little extra time for JavaScript to render *after* initial elements are found
        time.sleep(random.uniform(2, 5)) # Slightly reduced delay range

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Use the same domain-specific extraction logic
        domain = urlparse(url).netloc.lower()
        
        content = None
        if 'cio.com' in domain:
            content = _extract_cio_content(soup)
        elif 'csoonline.com' in domain:
            content = _extract_csoonline_content(soup)
        elif 'securityweek.com' in domain:
            content = _extract_securityweek_content(soup)
        elif 'thehackernews.com' in domain:
            content = _extract_hackernews_content(soup)
        elif 'krebsonsecurity.com' in domain:
            content = _extract_krebs_content(soup)
        
        if not content or len(content.strip()) < 100:
            logger.warning(f"Specific Selenium extraction failed or was too short for {url}. Falling back to general.")
            content = _extract_general_content(soup)
        
        if content and len(content.strip()) > 100:
            return content
        else:
            logger.error(f"Scraped content from {url} via Selenium was empty or too short. (Length: {len(content.strip()) if content else 0})")
            return None

    except TimeoutException as e:
        logger.error(f"Selenium Timeout error for {url}: Page content did not load in time. {e}")
        return None
    except WebDriverException as e:
        logger.error(f"Selenium WebDriver error during scraping {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during Selenium scraping {url}: {e}")
        return None