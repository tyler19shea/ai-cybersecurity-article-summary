from openai import OpenAI
from dotenv import load_dotenv
from newspaper import Article
import feedparser
import datetime
import logging
import atexit
from sendemail import sendemail

load_dotenv()
client=OpenAI()

RSS_URLS = ["https://krebsonsecurity.com/feed",
            "https://feeds.feedburner.com/TheHackersNews?format=xml",
            "https://isc.sans.edu/rssfeed_full.xml",
            "https://0dayfans.com/feed.rss"]

MESSAGE_FILE = "message.md"
PROCESSED_LINKS_FILE = "processed_links.txt"

logging.basicConfig(filename="CyberBot.log",format="%(asctime)s - %(levelname)s - %(message)s",filemode="a", level=logging.INFO)
def log_exit():
    logging.info("Exiting...")
atexit.register(log_exit)

def load_system_prompt():
    try:
        with open("./system_prompt", "r") as file:
            return file.read()
    except FileNotFoundError:
        error_message = "Error: The system_prompt file was not found."
        print(error_message)
        logging.error(error_message)
    except Exception:
        error_message = "An unexpected error occurred while loading system_prompt."
        print(error_message)
        logging.error(error_message, exc_info=True)
    return None

def load_processed_links():
    """Loads processed links from a file."""
    try:
        with open(PROCESSED_LINKS_FILE, "r") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_processed_links(links):
    """Saves processed links to a file."""
    with open(PROCESSED_LINKS_FILE, "a") as f:
        f.write("\n")
        for link in links:
            f.write(link + "\n")

def analyze_articles_with_openai(system_prompt, articles_text):
    """Analyzes the article text using OpenAI's API."""
    if not articles_text:
        return "No articles to analyze."
    try:
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": articles_text}
            ],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception:
        logging.error("Error during OpenAI API call", exc_info=True)
        return "Error during OpenAI API call. See log for details."

def fetch_hn_feed(url, limit=10):
    """Fetch and parse the RSS feed."""
    feed = feedparser.parse(url)
    return feed.entries[:limit]

def is_recent(entry, days=1):
    """Checks if an RSS feed entry was published within the last 'days' (default: 1 for yesterday)."""
    if hasattr(entry, 'published_parsed'):
        published_date = datetime.datetime(*entry.published_parsed[:6])
        now = datetime.datetime.now()
        delta = now - published_date
        return delta.days <= days
    return False

def get_article_text(entry):
        try:
            article = Article(entry.link)
            article.download()
            article.parse()
            return article.text
        except Exception:
            logging.error(f"Failed to download or parse {entry.link}", exc_info=True)
            return None

def main():
    system_prompt = load_system_prompt()
    if not system_prompt:
        return

    processed_links = load_processed_links()
    logging.info(f"Loaded {len(processed_links)} processed links.")

    logging.info("Gathering feeds...")
    all_feeds = []
    for url in RSS_URLS:
        all_feeds += fetch_hn_feed(url)
    
    logging.info("Getting article texts if within a day...")
    articles = []
    new_links = []
    for entry in all_feeds:
        if is_recent(entry) and entry.link not in processed_links:
            article_text = get_article_text(entry)
            if article_text:
                articles.append({'title': entry.title, 'text': article_text, 'url': entry.link})
                new_links.append(entry.link)

    if not articles:
        logging.info("No new articles found to analyze.")
        return

    # Format all articles into a single string for the prompt
    formatted_articles_string = ""
    for i, article in enumerate(articles, 1):
        formatted_articles_string += f"--- ARTICLE {i} ---\n"
        formatted_articles_string += f"Title: {article['title']}\n\n"
        formatted_articles_string += f"{article['text']}\n\n"
        formatted_articles_string += f"url: {article['url']}\n\n"

    print("Analyzing articles... This may take a moment.")
    logging.info("Analyzing articles with OpenAI...")
    analysis_result = analyze_articles_with_openai(system_prompt, formatted_articles_string)
    logging.info(f"Writing analysis to {MESSAGE_FILE}")
    with open(MESSAGE_FILE, "w") as f:
        f.write("#CYBERSECURITY ARTICLE ANALYSIS REPORT\n")
        f.write(analysis_result)
    
    save_processed_links(new_links)
    logging.info(f"Saved {len(new_links)} new links to {PROCESSED_LINKS_FILE}.")

    logging.info("Sending Email to users...")
    sendemail(MESSAGE_FILE)


if __name__ == '__main__':
    main()
