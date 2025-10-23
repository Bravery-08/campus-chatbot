"""
Crawls a certain website for certain depth and saves paragraph contents to data.txt
"""

from pypdf import PdfReader
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3
from urllib.parse import urlparse
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

visited = set()

content_classes_map = {"chennai.vit.ac.in": "col-md-12",
                       "vit.ac.in": "elementor-widget-container"}

skip_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico'}

start_url = 'https://chennai.vit.ac.in'
headers = {"User-Agent": "Mozilla/5.0 (compatible; VITWebCrawler/1.0)"}
response = requests.get(start_url, verify=False, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
dont_crawl = set()

news_div = soup.find('div', class_='news')
if news_div:
    for a in news_div.find_all('a', href=True):
        full_url = urljoin(start_url, a['href'])
        dont_crawl.add(full_url)


def save_content(url, soup):

    domain = urlparse(url).netloc

    try:
        body_div = None
        if domain in content_classes_map:
            body_div = soup.find('div', class_=content_classes_map[domain])
        else:
            body_div = soup.find('body')
        if not body_div:
            print(f"No content could be retrieved from {url}\n")
            return

        paragraphs = body_div.find_all('p')

        texts = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) >= 150:
                texts.append(text)

        filename = 'data.txt'
        with open(filename, 'a', encoding='utf-8') as f:
            for line in texts:
                f.write(line + '\n')

    except Exception as e:
        print(f"Error saving content from {url}: {e}")


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text_blocks = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_blocks.extend(text.split('\n\n'))
    return text_blocks


def handle_pdf(url):
    response = requests.get(url, verify=False, headers=headers)
    temp_pdf = 'temp.pdf'
    with open(temp_pdf, 'wb') as f:
        f.write(response.content)
    try:
        paragraphs = extract_text_from_pdf(temp_pdf)
        with open('data.txt', 'a', encoding='utf-8') as out:
            for paragraph in paragraphs:
                if len(paragraph) >= 150:
                    out.write(paragraph.strip().replace('\n', ' ') + '\n')
    finally:
        os.remove(temp_pdf)


def crawl(url, depth):

    if depth == 0:
        return
    try:
        visited.add(url)
        headers = {"User-Agent": "Mozilla/5.0 (compatible; VITWebCrawler/1.0)"}
        response = requests.get(url, verify=False, headers=headers)
        time.sleep(1)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Crawling URL: {url}")

        save_content(url, soup)

        for link in soup.find_all('a', href=True):

            href = link.get('href')
            full_url = urljoin(url, href)
            if full_url in dont_crawl or any(full_url.lower().endswith(ext) for ext in skip_extensions):
                continue
            if full_url.lower().endswith('.pdf') and full_url not in visited and "vit" in full_url:
                try:
                    print(f"Handling PDF: {full_url}")
                    handle_pdf(full_url)
                    visited.add(full_url)
                except Exception as e:
                    print(f"Failed to handle PDF {full_url}: {e}")
                continue
            try:
                href = link.get('href')
                full_url = urljoin(url, href)
                if full_url.startswith('http') and full_url not in visited and "vit" in full_url:
                    crawl(full_url, depth - 1)
            except Exception as e:
                print(f"Failed to crawl {href}: {e}")

    except Exception as e:
        print(f"Failed to crawl {url}: {e}\n")


start_url = 'https://chennai.vit.ac.in'
crawl(start_url, 2)
