import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import time

class RSSFeedDiscovery:
    def __init__(self, timeout: int = 15, user_agent: str = "RSS Discovery Bot 1.0"):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        
        # Common RSS feed paths to check
        self.common_paths = [
            '/rss',
            '/rss.xml',
            '/feed',
            '/feed.xml',
            '/feeds',
            '/index.xml',
            '/atom.xml',
            '/rss/feed',
            '/blog/feed',
            '/news/feed'
        ]
    
    def normalize_url(self, url: str) -> str:
        """Add https:// if no protocol specified"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def is_valid_rss_feed(self, feed_url: str) -> Dict[str, any]:
        """Check if URL returns valid RSS/Atom XML"""
        try:
            response = self.session.get(feed_url, timeout=self.timeout)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            # Check content type
            if not any(ct in content_type for ct in ['xml', 'rss', 'atom']):
                return {'valid': False, 'error': f'Invalid content type: {content_type}'}
            
            # Try to parse XML
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError as e:
                return {'valid': False, 'error': f'XML parse error: {str(e)}'}
            
            # Check if it's RSS or Atom
            feed_type = None
            title = "Unknown"
            
            if root.tag == 'rss':
                feed_type = 'RSS'
                title_elem = root.find('.//channel/title')
                if title_elem is not None:
                    title = title_elem.text or "RSS Feed"
            elif root.tag == 'feed' or root.tag.endswith('}feed'):
                feed_type = 'Atom'
                title_elem = root.find('.//{*}title')
                if title_elem is not None:
                    title = title_elem.text or "Atom Feed"
            else:
                return {'valid': False, 'error': f'Not RSS/Atom format. Root tag: {root.tag}'}
            
            return {
                'valid': True,
                'type': feed_type,
                'title': title,
                'url': feed_url,
                'content_type': content_type
            }
            
        except requests.RequestException as e:
            return {'valid': False, 'error': f'Request failed: {str(e)}'}
    
    def find_feeds_in_html(self, base_url: str) -> List[str]:
        """Parse HTML to find RSS feed links"""
        try:
            response = self.session.get(base_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            feed_urls = []
            
            # Look for link tags with RSS/Atom types
            link_tags = soup.find_all('link', {
                'rel': 'alternate',
                'type': ['application/rss+xml', 'application/atom+xml', 'application/xml+rss']
            })
            
            for link in link_tags:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    feed_urls.append(full_url)
            
            return feed_urls
            
        except requests.RequestException as e:
            print(f"Error fetching HTML from {base_url}: {e}")
            return []
    
    def discover_rss_feeds(
        self, 
        base_url: str, 
        check_common_paths: bool = True,
        verify_feeds: bool = True
    ) -> List[Dict[str, any]]:
        """
        Main function to discover RSS feeds for a website
        
        Args:
            base_url: Website URL to check
            check_common_paths: Whether to check common RSS paths
            verify_feeds: Whether to validate discovered feeds
            
        Returns:
            List of discovered feeds with metadata
        """
        base_url = self.normalize_url(base_url)
        print(f"\n🔍 Discovering RSS feeds for: {base_url}")
        
        discovered_feeds = []
        checked_urls = set()
        
        # Method 1: Parse HTML for feed links
        print("📄 Checking HTML for feed links...")
        html_feeds = self.find_feeds_in_html(base_url)
        
        for feed_url in html_feeds:
            if feed_url not in checked_urls:
                checked_urls.add(feed_url)
                if verify_feeds:
                    result = self.is_valid_rss_feed(feed_url)
                    if result['valid']:
                        discovered_feeds.append(result)
                        print(f"  ✅ Found: {result['title']} ({result['type']}) - {feed_url}")
                    else:
                        print(f"  ❌ Invalid: {feed_url} - {result['error']}")
                else:
                    discovered_feeds.append({'url': feed_url, 'source': 'HTML'})
        
        # Method 2: Check common RSS paths
        if check_common_paths:
            print("🔗 Checking common RSS paths...")
            for path in self.common_paths:
                feed_url = urljoin(base_url, path)
                if feed_url not in checked_urls:
                    checked_urls.add(feed_url)
                    if verify_feeds:
                        result = self.is_valid_rss_feed(feed_url)
                        if result['valid']:
                            discovered_feeds.append(result)
                            print(f"  ✅ Found: {result['title']} ({result['type']}) - {feed_url}")
                    else:
                        # For common paths, just check if URL exists
                        try:
                            response = self.session.head(feed_url, timeout=5)
                            if response.status_code == 200:
                                discovered_feeds.append({'url': feed_url, 'source': 'Common Path'})
                        except:
                            pass
        
        if not discovered_feeds:
            print("  ❌ No RSS feeds found")
        else:
            print(f"  🎉 Total feeds discovered: {len(discovered_feeds)}")
        
        return discovered_feeds


def test_cybersecurity_sites():
    """Test the RSS discovery on cybersecurity websites"""
    
    test_sites = [
        'https://www.theregister.com/',
    ]
    
    finder = RSSFeedDiscovery()
    all_results = {}
    
    for site in test_sites:
        try:
            feeds = finder.discover_rss_feeds(site)
            all_results[site] = feeds
            time.sleep(1)  # Be polite to servers
        except Exception as e:
            print(f"Error processing {site}: {e}")
            all_results[site] = []
    
    # Summary report
    print("\n" + "="*60)
    print("📊 DISCOVERY SUMMARY")
    print("="*60)
    
    for site, feeds in all_results.items():
        print(f"\n🌐 {site}")
        if feeds:
            for i, feed in enumerate(feeds, 1):
                if 'title' in feed:
                    print(f"  {i}. {feed['title']} ({feed['type']})")
                    print(f"     URL: {feed['url']}")
                else:
                    print(f"  {i}. {feed['url']}")
        else:
            print("  No feeds found")
    
    return all_results


# Run the test
if __name__ == "__main__":
    results = test_cybersecurity_sites()