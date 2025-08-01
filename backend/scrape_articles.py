# blog/management/commands/scrape_articles.py

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
import re # Make sure this is imported for the text cleaning regex

class Command(BaseCommand):
    help = 'Scrapes the main article content from a given URL.'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='The URL of the article to scrape.')
        parser.add_argument('--output-file', type=str, help='Optional: Path to save the scraped content to a text file.')

    def handle(self, *args, **options):
        url = options['url']
        output_file = options['output_file']

        self.stdout.write(self.style.NOTICE(f'Attempting to scrape content from: {url}'))

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            article_content = self._extract_main_content(soup)

            if not article_content:
                # Add more specific debugging if content is not found
                self.stdout.write(self.style.ERROR(f"Could not find main article content on {url}. Inspect HTML of the target page for div.articlebody.clear.cf and its children."))
                # You might want to print a snippet of the raw HTML here for deeper debugging
                # self.stdout.write(self.style.ERROR(f"Snippet of HTML body: {response.text[:2000]}"))
                raise CommandError(f"Scraping failed for {url}.")

            self.stdout.write(self.style.SUCCESS(f'Successfully scraped content from {url}'))

            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(article_content)
                self.stdout.write(self.style.SUCCESS(f'Content saved to: {output_file}'))
            else:
                self.stdout.write(self.style.HTTP_INFO('\n--- Scraped Content Preview (first 500 chars) ---\n'))
                self.stdout.write(article_content[:500] + '...' if len(article_content) > 500 else article_content)
                self.stdout.write(self.style.HTTP_INFO('\n--- End Preview ---\n'))

        except requests.exceptions.RequestException as e:
            raise CommandError(f"Network or HTTP error during scraping: {e}")
        except Exception as e:
            raise CommandError(f"An unexpected error occurred: {e}")

    def _extract_main_content(self, soup):
        """
        Custom extraction for thehackernews.com based on identified HTML structure.
        Looks for 'div.articlebody.clear.cf' and concatenates text from its relevant children.
        """
        # 1. Find the main article body container
        article_body_div = soup.select_one('div.articlebody.clear.cf')

        if not article_body_div:
            # Fallback to general selectors if the specific div isn't found
            self.stdout.write(self.style.WARNING("Specific 'div.articlebody.clear.cf' not found. Trying general selectors."))
            # Call the old general logic if the specific one fails
            return self._extract_general_content(soup)


        # 2. Define tags that typically contain readable content
        # Add other tags if you see them holding content (e.g., 'li' for lists)
        content_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'li', 'span', 'b', 'strong']

        extracted_paragraphs = []

        # 3. Iterate through all child elements of the article body div
        # and collect text from relevant tags.
        for element in article_body_div.find_all(content_tags):
            # Clean up the text by removing extra spaces and newlines
            text = element.get_text(separator=' ', strip=True) # Use space separator to avoid words merging
            if text:
                extracted_paragraphs.append(text)

        # 4. Join the extracted parts. Use double newlines to simulate paragraph breaks.
        full_text = '\n\n'.join(extracted_paragraphs)

        # 5. Clean up the final text further:
        # Remove excessive whitespace and normalize newlines
        full_text = re.sub(r'\s*\n\s*', '\n', full_text).strip() # Replace multi-line breaks with single
        full_text = re.sub(r'\n{3,}', '\n\n', full_text) # Ensure no more than two newlines between blocks

        return full_text if full_text else None

    # This method is extracted from the previous version as a fallback
    def _extract_general_content(self, soup):
        """
        A general fallback method to extract content using common HTML patterns.
        Used if the specific thehackernews.com selector fails.
        """
        selectors = [
            'div.entry-content',
            'div.article-content',
            'div.post-content',
            'div[itemprop="articleBody"]',
            'article',
            'div.story-body',
            'div.main-content',
            'section.article-body',
            'body'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                for script_or_style in element(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    script_or_style.decompose()

                text = element.get_text(separator='\n', strip=True)
                text = re.sub(r'\n\s*\n', '\n\n', text)
                return text.strip()

        paragraphs = soup.find_all('p')
        if paragraphs:
            full_text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            if full_text:
                return full_text.strip()

        return None