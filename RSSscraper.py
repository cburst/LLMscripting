import sys
import time
import csv
import re
import unicodedata
import feedparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser


def format_publication_date(published):
    """Convert the publication date to 'yyyymmddhhmm' format."""
    if not published or published == "No Date":
        return "unknown_date"
    try:
        return parser.parse(published).strftime("%Y%m%d%H%M")
    except Exception as e:
        print(f"Error formatting publication date: {e}")
        return "unknown_date"


def extract_date_from_html(soup):
    """Extract the most reliable date and time from the HTML content."""
    print("Attempting to extract date and time from HTML content...")

    # 1. Check meta tags
    meta_tags = [
        {"property": "article:published_time"},
        {"property": "og:published_time"},
        {"name": "pubdate"},
        {"name": "publish_date"},
        {"name": "date"},
    ]
    for tag in meta_tags:
        meta = soup.find("meta", tag)
        if meta and meta.get("content"):
            try:
                print(f"Found date in meta tag: {meta['content']}")
                return parser.parse(meta["content"]).strftime("%Y%m%d%H%M")
            except Exception as e:
                print(f"Error parsing meta tag date: {e}")

    # 2. Check for <span> elements with date-like text
    spans = soup.find_all("span")
    for span in spans:
        date_text = span.get_text(strip=True)
        if re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", date_text):
            try:
                print(f"Found date in span: {date_text}")
                return parser.parse(date_text).strftime("%Y%m%d%H%M")
            except Exception as e:
                print(f"Error parsing span date: {e}")

    # 3. Regex fallback in the entire HTML text
    content = soup.get_text()
    date_time_pattern = re.compile(
        r"(\b\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}\b|\b\d{4}-\d{2}-\d{2}\b)"
    )
    match = date_time_pattern.search(content)
    if match:
        try:
            date_str = match.group()
            if ":" not in date_str:  # Default time if only date is found
                date_str += " 00:00"
            print(f"Found date using regex fallback: {date_str}")
            return parser.parse(date_str).strftime("%Y%m%d%H%M")
        except Exception as e:
            print(f"Error parsing fallback date: {e}")

    print("No date found in HTML content.")
    return "unknown_date"


def extract_date(rss_entry, soup=None):
    """
    Try to extract the date:
    1. From the RSS feed (published or updated fields).
    2. From the HTML content, if soup is provided.
    """
    # Attempt to get date from the RSS entry
    for field in ["published", "updated", "pubDate"]:
        if field in rss_entry and rss_entry[field]:
            date = format_publication_date(rss_entry[field])
            if date != "unknown_date":
                print(f"Found date in RSS feed ({field}): {date}")
                return date

    # Attempt to get date from the HTML content
    if soup:
        return extract_date_from_html(soup)

    # Default to unknown date
    print("No date found in RSS entry or HTML content.")
    return "unknown_date"


def sanitize_content(content):
    """Remove tabs, replace problematic symbols, remove accents, and normalize whitespace for analysis."""
    sanitized = content.replace("\t", " ")
    sanitized = unicodedata.normalize('NFKD', sanitized).encode('utf-8', 'ignore').decode('utf-8')
    sanitized = re.sub(r"\s+", " ", sanitized)
    return sanitized.strip()


def split_content_for_tsv(content, publication_date):
    """Split content into chunks of 3600 characters or less for TSV."""
    chunks = []
    suffix = 1
    while len(content) > 3600:
        split_index = content.rfind(" ", 0, 3600)
        if split_index == -1:
            split_index = 3600
        chunk = content[:split_index].strip()
        chunks.append((f"{publication_date}_{suffix}", chunk))
        content = content[split_index:].strip()
        suffix += 1
    if content:
        chunks.append((f"{publication_date}_{suffix}", content))
    return chunks


def sanitize_filename(name):
    """Sanitize filenames to remove or replace special characters."""
    return re.sub(r'[\/:*?"<>|]', '_', name)


def download_from_rss(rss_url, keywords=None, max_articles=100):
    """Fetch and process articles from the RSS feed."""
    feed = feedparser.parse(rss_url)
    articles = feed.entries
    filtered_articles = articles if not keywords else [
        article for article in articles if any(keyword.lower() in article.get("title", "").lower() for keyword in keywords)
    ]

    # Generate filenames with keywords or "all_articles"
    sanitized_keywords = sanitize_filename("_".join(keywords) if keywords else "all_articles")
    csv_filename = f"{sanitized_keywords}.csv"
    tsv_filename = f"{sanitized_keywords}-for-analysis-raw.tsv"

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["Link", "Title", "Publication", "Publication Date", "Content"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        with open(tsv_filename, mode="w", newline="", encoding="utf-8") as tsv_file:
            tsv_writer = csv.writer(tsv_file, delimiter='\t')
            tsv_writer.writerow(["Publication Date", "Content"])  # Write TSV headers

            options = Options()
            options.headless = True
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            for i, article in enumerate(filtered_articles[:max_articles], start=1):
                title = article.get("title", "No Title")
                link = article.get("link", "No Link")
                print(f"Processing article {i}: {title}")

                try:
                    # Load the article HTML for scraping
                    driver.get(link)
                    time.sleep(2)
                    soup = BeautifulSoup(driver.page_source, "html.parser")

                    # Extract the date
                    formatted_date = extract_date(article, soup)

                    # Extract the article content
                    paragraphs = soup.find_all("p")
                    article_text = "\n".join(para.get_text() for para in paragraphs)
                    if not article_text.strip():
                        print(f"Skipping empty article at {link}")
                        continue

                    sanitized_content = sanitize_content(article_text)
                    writer.writerow({
                        "Link": link,
                        "Title": title,
                        "Publication": "",
                        "Publication Date": formatted_date,
                        "Content": sanitized_content,
                    })

                    # Write to TSV in chunks
                    chunks = split_content_for_tsv(sanitized_content, formatted_date)
                    for chunk_date, chunk_content in chunks:
                        tsv_writer.writerow([chunk_date, chunk_content])

                    print(f"Processed article {i}: {title}")

                except Exception as e:
                    print(f"Failed to process article {link}: {e}")

            driver.quit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <rss_url> [<keyword1,keyword2,...>]")
        sys.exit(1)

    rss_url = sys.argv[1]
    keywords = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    download_from_rss(rss_url, keywords)