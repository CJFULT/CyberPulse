# backend/discover_urls.py

import feedparser
import time
import random
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from urllib.parse import urlparse
# Make sure your scraper utility is in the backend folder
from scraper import scrape_article_content, initialize_chrome_driver

# --- Initialize Supabase Client ---
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
# Use the SERVICE key for admin-level access to bypass RLS
supabase_key = os.getenv("SUPABASE_SERVICE_KEY") 
if not supabase_url or not supabase_key:
    raise ValueError("Supabase credentials must be set in the .env file.")
supabase: Client = create_client(supabase_url, supabase_key)
# --- End of Initialization ---

CYBERSECURITY_RSS_FEEDS = [
    "https://www.securityweek.com/feed",
    "https://www.bleepingcomputer.com/feed/",
    "https://darkreading.com/rss.xml",
]

SELENIUM_REQUIRED_DOMAINS = [
    'securityweek.com',
    'darkreading.com',
]

def discover_and_scrape(max_articles_per_feed=5):
    """
    Discovers new URLs from RSS feeds, scrapes them, and stores in Supabase.
    """
    print('Starting URL discovery and content scraping...')
    total_new_articles = 0

    chrome_driver = None  # Initialize driver to None
    try:
        # Initialize driver only if Selenium might be needed
        if any(any(d in feed for d in SELENIUM_REQUIRED_DOMAINS) for feed in CYBERSECURITY_RSS_FEEDS):
            print("Initializing Chrome WebDriver for potential Selenium usage...")
            chrome_driver = initialize_chrome_driver()

        for feed_url in CYBERSECURITY_RSS_FEEDS:
            print(f'\nProcessing feed: {feed_url}')
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                print(f'  No entries found in feed: {feed_url}')
                continue

            for entry in feed.entries[:max_articles_per_feed]:
                link = entry.link
                
                # --- NEW: Check if URL exists in Supabase ---
                response = supabase.table('processed_urls').select('url').eq('url', link).execute()
                if response.data:
                    print(f'  URL already processed (skipping): {link}')
                    continue
                # --- End of Check ---

                print(f'  Attempting to scrape new article: {link}')
                
                domain = urlparse(link).netloc.lower()
                force_selenium = any(d in domain for d in SELENIUM_REQUIRED_DOMAINS)

                content, _ = scrape_article_content(
                    link, 
                    chrome_driver=chrome_driver, 
                    force_selenium_for_this_url=force_selenium
                )

                if content:
                    article_title = entry.title if hasattr(entry, 'title') else 'No Title Available'
                    
                    try:
                        # --- NEW: Insert into Supabase 'articles' table ---
                        supabase.table('articles').insert({
                            'url': link,
                            'title': article_title,
                            'raw_content': content
                        }).execute()
                        
                        # --- NEW: Insert into Supabase 'processed_urls' table ---
                        supabase.table('processed_urls').insert({'url': link}).execute()
                        
                        total_new_articles += 1
                        print(f'  ✅ Successfully scraped and stored: "{article_title[:60]}..."')
                    except Exception as db_e:
                        print(f'  Database error storing {link}: {db_e}')
                else:
                    print(f'  ❌ Failed to scrape content from {link}.')
                
                time.sleep(random.uniform(1, 3))

    finally:
        if chrome_driver:
            print("Quitting Chrome WebDriver...")
            chrome_driver.quit()

    print(f'\n🎉 Finished URL discovery. New articles stored: {total_new_articles}')

if __name__ == "__main__":
    discover_and_scrape()