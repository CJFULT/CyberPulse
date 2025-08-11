# backend/discover_urls.py

import feedparser
import time
import random
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from urllib.parse import urlparse
# Make sure your scraper and new analyzer are in the backend folder
from scraper import scrape_article_content, initialize_chrome_driver
from analyzer import extract_key_excerpts_by_similarity

# --- Initialize Supabase Client ---
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
if not supabase_url or not supabase_key:
    raise ValueError("Supabase credentials must be set in the .env file.")
supabase: Client = create_client(supabase_url, supabase_key)
# --- End of Initialization ---

CYBERSECURITY_RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://krebsonsecurity.com/feed/",
    "https://www.securityweek.com/feed",
    "https://cyble.com/feed/",
    "https://www.itsecurityguru.org/feed/",
    "https://searchsecurity.techtarget.com/rss/Security-Wire-Daily-News.xml",
    "https://www.schneier.com/feed/",
    "https://www.wired.com/feed/category/security/latest/rss",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://techcrunch.com/feed/",
    "https://ainowinstitute.org/feed",
    "https://cdt.org/area-of-focus/ai-policy-governance/feed/",
    "https://cdt.org/area-of-focus/cybersecurity-standards/feed/",
    "https://www.cisa.gov/news-events/cybersecurity-advisories/rss",
    "https://www.nist.gov/blogs/cybersecurity-insights/rss.xml",
    "https://www.silicon.co.uk/news/e-innovation/artificial-intelligence/feed",
]

SELENIUM_REQUIRED_DOMAINS = [
    'securityweek.com',
    'darkreading.com',
    'itsecurityguru.org',
    'cdt.org',
    'cisa.gov',
]

# --- NEW: Whitelist for domains where full content is permissible ---
# Articles from these domains will not be summarized and the full
# text will be stored in the database.
FULL_CONTENT_ALLOWED_DOMAINS = [
    'www.nist.gov',
    'www.cisa.gov',
    # Add any other government or open-licensed domains here
]

def discover_and_scrape(max_articles_per_feed=30):
    """
    Discovers URLs, scrapes them, and either analyzes for excerpts or stores
    the full content based on a domain whitelist.
    """
    print('Starting URL discovery, scraping, and analysis...')
    total_new_articles = 0

    chrome_driver = None
    try:
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
                
                response = supabase.table('processed_urls').select('url').eq('url', link).execute()
                if response.data:
                    print(f'  URL already processed (skipping): {link}')
                    continue

                print(f'  Attempting to scrape new article: {link}')
                
                domain = urlparse(link).netloc.lower()
                force_selenium = any(d in domain for d in SELENIUM_REQUIRED_DOMAINS)

                content = scrape_article_content(
                    link, 
                    chrome_driver=chrome_driver, 
                    force_selenium_for_this_url=force_selenium
                )

                if content:
                    article_title = entry.title if hasattr(entry, 'title') else 'No Title Available'
                    content_to_store = None # --- MODIFIED: Initialize variable

                    # --- MODIFIED: Conditional logic based on domain whitelist ---
                    if domain in FULL_CONTENT_ALLOWED_DOMAINS:
                        print(f"  - Domain '{domain}' is on the whitelist. Storing full content.")
                        content_to_store = content
                    else:
                        print(f"  - Analyzing content for: \"{article_title[:60]}...\"")
                        content_to_store = extract_key_excerpts_by_similarity(content, article_title)
                    # --- End of modification ---
                    
                    if not content_to_store:
                        print(f'  ❌ Failed to process content from {link}. Skipping.')
                        continue
                    
                    try:
                        # --- MODIFIED: Use the 'content_to_store' variable ---
                        supabase.table('articles').insert({
                            'url': link,
                            'title': article_title,
                            'raw_content': content_to_store # This will hold either excerpts or full text
                        }).execute()
                        
                        supabase.table('processed_urls').insert({'url': link}).execute()
                        
                        total_new_articles += 1
                        print(f'  ✅ Successfully stored content for: "{article_title[:60]}..."')
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
