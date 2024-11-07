import sys
import os
import time
import csv
import re
import unicodedata
from pygooglenews import GoogleNews
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime

def format_publication_date(published):
    """Convert the publication date to 'yyyymmddhhmm' format."""
    try:
        # Parse the date string, which is typically in RFC 2822 format
        dt = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%Y%m%d%H%M")
    except ValueError:
        return ""  # Return an empty string if the date format is unexpected

def sanitize_content(content):
    """Remove tabs, replace problematic symbols, remove accents, and normalize whitespace for analysis."""
    # Remove tabs
    sanitized = content.replace("\t", " ")
    # Replace various quotation marks with a standard apostrophe
    sanitized = sanitized.replace('"', "'").replace("“", "'").replace("”", "'")
    sanitized = sanitized.replace("‘", "'").replace("’", "'")
    # Replace en dash and em dash with hyphen
    sanitized = sanitized.replace("–", "-").replace("—", "-")
    # Replace ellipses with a single period
    sanitized = sanitized.replace("…", ".")
    # Replace non-breaking spaces with regular space
    sanitized = sanitized.replace("\xa0", " ")
    # Remove accented characters by normalizing to ASCII
    sanitized = unicodedata.normalize('NFKD', sanitized).encode('ASCII', 'ignore').decode('ASCII')
    # Normalize whitespace
    sanitized = re.sub(r"\s+", " ", sanitized)
    return sanitized.strip()

def split_content_for_tsv(content, publication_date):
    """Split content into chunks of 1000 characters or less for TSV, 
    appending numbers to the publication date for each chunk."""
    chunks = []
    suffix = 1
    
    while len(content) > 3600:
        # Find the last space before 1000 characters
        split_index = content.rfind(" ", 0, 3600)
        if split_index == -1:
            split_index = 3600  # Fall back to splitting exactly at 1000 if no space is found
        
        # Extract the chunk up to the split index
        chunk = content[:split_index].strip()
        chunks.append((f"{publication_date}{suffix}", chunk))
        
        # Prepare for the next chunk
        content = content[split_index:].strip()
        suffix += 1
    
    # Append the remaining content with the latest suffix
    chunks.append((f"{publication_date}{suffix}", content))
    return chunks

def download_full_articles(keywords, max_articles=100):
    # Initialize GoogleNews and search
    gn = GoogleNews()
    search_query = " OR ".join(keywords)
    search = gn.search(search_query)
    articles = search['entries'][:max_articles]

    # CSV and TSV file names based on keywords
    csv_filename = "_".join(keywords) + ".csv"
    tsv_filename = "_".join(keywords) + "-for-analysis-raw.tsv"

    # Prepare the main CSV file
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["Link", "Title", "Publication", "Publication Date", "Content"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Prepare the TSV file for analysis
        with open(tsv_filename, mode="w", newline="", encoding="utf-8") as tsv_file:
            tsv_writer = csv.writer(tsv_file, delimiter='\t')
            tsv_writer.writerow(["Publication Date", "Content"])  # Write TSV headers

            # Set up Selenium with webdriver-manager for automatic driver management
            options = Options()
            options.headless = True
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            # Process each article
            for i, article in enumerate(articles, start=1):
                raw_title = article.get('title', 'No Title')
                redirect_link = article.get('link', 'No Link')
                published = article.get('published', 'No Date')

                # Format the publication date for analysis
                formatted_date = format_publication_date(published)

                # Split the title and publication if a dash is present
                if " - " in raw_title:
                    title, publication = raw_title.rsplit(" - ", 1)
                else:
                    title, publication = raw_title, ""  # No publication found

                try:
                    # Use Selenium to load the article page fully from the redirect link
                    driver.get(redirect_link)
                    time.sleep(2)  # Allow time for page to load

                    # Capture the final URL after any redirects
                    final_url = driver.current_url

                    # Parse the page source with BeautifulSoup
                    article_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    paragraphs = article_soup.find_all('p')
                    article_text = "\n".join([para.get_text() for para in paragraphs])

                    if not article_text.strip():
                        print(f"Skipping empty article at {final_url}")
                        continue

                    # Sanitize content for both CSV and TSV
                    sanitized_content = sanitize_content(article_text)

                    # Write the full article data to the CSV file
                    writer.writerow({
                        "Link": final_url,
                        "Title": title,
                        "Publication": publication,
                        "Publication Date": published,
                        "Content": sanitized_content
                    })

                    # Write split content chunks to the TSV file
                    if formatted_date:
                        content_chunks = split_content_for_tsv(sanitized_content, formatted_date)
                        for chunk_date, chunk_content in content_chunks:
                            tsv_writer.writerow([chunk_date, chunk_content])

                    print(f"Downloaded and saved article {i}: {title}")

                except Exception as e:
                    print(f"Failed to retrieve or parse {redirect_link}: {e}")

                time.sleep(1)  # Respectful delay to avoid being blocked

            driver.quit()
    print(f"Downloaded {min(len(articles), max_articles)} articles containing the keywords '{', '.join(keywords)}'.")

# Handle command-line arguments
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <keyword1,keyword2,...>")
        sys.exit(1)
    
    keywords = sys.argv[1].split(",")
    download_full_articles(keywords)