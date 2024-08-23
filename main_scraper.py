import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
import html2text
import re

class ImprovedDocScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited_urls = set()
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = True
        self.html2text.ignore_images = True
        self.common_elements = {}
        self.content_threshold = 0.8  # Adjust this value to fine-tune filtering

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.netloc == self.domain and parsed_url.path.startswith(urlparse(self.base_url).path)

    def normalize_url(self, url):
        return urldefrag(url)[0]

    def get_links(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        return [self.normalize_url(urljoin(self.base_url, link['href'])) for link in links if self.is_valid_url(urljoin(self.base_url, link['href']))]

    def extract_content(self, soup):
        # Remove common elements like navigation, footer, etc.
        for element in soup(['nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Extract the main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if main_content:
            return self.html2text.handle(str(main_content))
        return self.html2text.handle(soup.prettify())

    def identify_common_elements(self, content):
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                self.common_elements[line] = self.common_elements.get(line, 0) + 1

    def filter_common_elements(self, content):
        lines = content.split('\n')
        total_pages = len(self.visited_urls)
        filtered_lines = [line for line in lines if self.common_elements.get(line, 0) / total_pages < self.content_threshold]
        return '\n'.join(filtered_lines)

    def scrape_page(self, url):
        normalized_url = self.normalize_url(url)
        if normalized_url in self.visited_urls:
            return
        
        self.visited_urls.add(normalized_url)
        
        response = requests.get(normalized_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = self.extract_content(soup)
        
        self.identify_common_elements(content)
        
        for link in self.get_links(normalized_url):
            self.scrape_page(link)

    def save_filtered_content(self):
        with open('filtered_docs_2.txt', 'w', encoding='utf-8') as file:
            for url in self.visited_urls:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                content = self.extract_content(soup)
                filtered_content = self.filter_common_elements(content)
                
                file.write(f"URL: {url}\n")
                file.write(filtered_content)
                file.write("\n\n" + "="*50 + "\n\n")

def main():
    base_url = input("Enter the documentation website URL: ")
    scraper = ImprovedDocScraper(base_url)
    scraper.scrape_page(base_url)
    scraper.save_filtered_content()
    print(f"Number of urls: {len(scraper.visited_urls)}")
    print("\nScraping and filtering completed.")
    print("Filtered content saved to filtered_docs.txt")

if __name__ == "__main__":
    main()