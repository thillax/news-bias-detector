import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "BBC News": "http://feeds.bbc.co.uk/news/rss.xml",
    "Reuters": "https://www.reuters.com/finance",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "The Hindu": "https://www.thehindu.com/news/feeder/default.rss",
    "Times of India": "https://feed.timesofindia.com/rss/",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "NPR": "https://feeds.npr.org/1001/rss.xml"
}

class RSSFetcher:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_all_feeds(self) -> List[Dict]:
        all_articles = []
        for source_name, feed_url in RSS_FEEDS.items():
            logger.info(f"Fetching from {source_name}...")
            articles = self.fetch_feed(feed_url, source_name)
            all_articles.extend(articles)
            logger.info(f"✓ Got {len(articles)} articles from {source_name}")
        return all_articles
    
    def fetch_feed(self, feed_url: str, source_name: str) -> List[Dict]:
        articles = []
        try:
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                return articles
            
            for entry in feed.entries:
                article = self._parse_entry(entry, source_name)
                if article:
                    articles.append(article)
        except Exception as e:
            logger.error(f"Error fetching {source_name}: {str(e)}")
        return articles
    
    def _parse_entry(self, entry, source_name: str) -> Optional[Dict]:
        try:
            title = entry.get('title', 'Untitled')
            content = entry.get('summary', '')
            url = entry.get('link', '')
            author = entry.get('author', source_name)
            published_date = self._parse_date(entry)
            
            if not title or not url:
                return None
            
            article = {
                'title': title[:200],
                'source': source_name,
                'author': author[:100] if author else source_name,
                'published_date': published_date,
                'content': content[:5000],
                'url': url[:500],
                'topic': 'General',
                'category': 'News',
                'language': 'English'
            }
            return article
        except:
            return None
    
    def _parse_date(self, entry) -> datetime:
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6])
        except:
            pass
        return datetime.now()

def get_rss_articles() -> List[Dict]:
    fetcher = RSSFetcher()
    return fetcher.fetch_all_feeds()
