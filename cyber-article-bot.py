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

feed=[]
for url in RSS_URLS:
    feed += fetch_hn_feed(url)

for entry in feed:
    if is_recent(entry):
        article = Article(entry.link)
        article.download()
        article.parse()

        full_text = article.text
        if full_text != '':
            print(entry.published)
            print(f"TITLE: {entry.title}")
            # print(full_text)