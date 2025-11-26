from openai import OpenAI
from dotenv import load_dotenv
from newspaper import Article
import feedparser
import datetime
import logging
import atexit

load_dotenv()
client=OpenAI()

RSS_URLS = ["https://krebsonsecurity.com/feed",
            "https://feeds.feedburner.com/TheHackersNews?format=xml",
            "https://isc.sans.edu/rssfeed_full.xml",
            "https://0dayfans.com/feed.rss"]

logging.basicConfig(filename="CyberBot.log",format="%(asctime)s %(message)s",filemode="a", level=logging.INFO)
def log_exit():
    logging.info("Bot Stopped")
atexit.register(log_exit)

def load_system_prompt():
    try:
        with open("./system_prompt", "r") as file:
            return file.read()
    except FileNotFoundError:
        error_message = "Error: The file system_prompt was not found."
        print(error_message)
        logging.info(error_message)
    except Exception as e:
        error_message = f"An error occurred: {e}"
        print(error_message)
        logging.info(error_message)
    return None

def analyze_article_with_openai(system_prompt, article_text):
    """Analyzes the article text using OpenAI's API."""
    if not article_text:
        return "Article text is empty, skipping analysis."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": article_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error during OpenAI API call: {e}"

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
        article = Article(entry.link)
        article.download()
        article.parse()

        full_text = article.text
        if full_text != '':
            return full_text

def main():
    system_prompt = load_system_prompt()
    if not system_prompt:
        return

    feed=[]
    for url in RSS_URLS:
        feed += fetch_hn_feed(url)

    for entry in feed:
        if is_recent(entry):
            # print(f"Title: {entry.title}")
            article_text = get_article_text(entry)
            if article_text != None:
                print(f"Title: {entry.title}")
                summary = analyze_article_with_openai(system_prompt, article_text)
                print(f"Summary:\n{summary}\n")
                print(entry.link)
                print(entry.published)

if __name__ == '__main__':
    main()