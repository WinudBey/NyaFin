import feedparser
from typing import List, Dict, Optional
from core.logger import get_logger
from core.config import Config
from core.exceptions import ScraperError

logger = get_logger(__name__)

class NyaaScraper:
    """Handles fetching and filtering releases from Nyaa.si RSS feed."""
    
    def __init__(self, rss_url: str = Config.NYAA_RSS_URL, target_groups: List[str] = Config.TARGET_GROUPS):
        self.rss_url = rss_url
        self.target_groups = target_groups
        logger.debug(f"NyaaScraper initialized with URL: {self.rss_url}")
        logger.debug(f"Target groups: {self.target_groups}")

    def fetch_latest(self) -> List[Dict]:
        """
        Fetches the latest items from the RSS feed.
        
        Returns:
            List of parsed items (dictionaries).
        """
        logger.debug("Fetching RSS feed...")
        try:
            feed = feedparser.parse(self.rss_url)
            if feed.bozo:
                # bozo=1 indicates malformed XML or connection error in feedparser
                raise ScraperError("Failed to parse RSS feed correctly.")
            
            items = feed.get('entries', [])
            logger.debug(f"Successfully fetched {len(items)} items from RSS.")
            return items
        except Exception as e:
            logger.error(f"Error fetching RSS: {e}")
            raise ScraperError(f"Error fetching RSS: {e}")

    def filter_items(self, items: List[Dict]) -> List[Dict]:
        """
        Filters items based on target release groups to ensure softsubs are likely present.
        
        Args:
            items: List of dictionaries from feedparser.
            
        Returns:
            Filtered list of items.
        """
        logger.debug("Filtering RSS items...")
        filtered = []
        for item in items:
            title = item.get('title', '')
            link = item.get('link', '') # This is the torrent file link
            
            # Check if any target group is in the title
            if any(group.lower() in title.lower() for group in self.target_groups):
                filtered.append({
                    'title': title,
                    'torrent_url': link,
                    'info_hash': item.get('nyaa_infohash', '')
                })
        
        logger.debug(f"Filtered {len(filtered)} items out of {len(items)}.")
        return filtered

    def get_download_candidates(self) -> List[Dict]:
        """
        High level method to fetch and filter in one step.
        """
        items = self.fetch_latest()
        return self.filter_items(items)
