import json
import os
import re
from typing import List, Dict, Tuple, Optional
from core.logger import get_logger
from core.config import Config

logger = get_logger(__name__)

class Tracker:
    """Manages tracked series and episode history."""
    def __init__(self):
        self.db_path = os.path.join(Config.DATA_DIR, "series_db.json")
        self.db = self._load_db()

    def _load_db(self) -> dict:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load series DB: {e}")
        return {"tracked_series": {}}

    def _save_db(self):
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.db, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save series DB: {e}")

    def add_series(self, series_name: str):
        if series_name not in self.db["tracked_series"]:
            self.db["tracked_series"][series_name] = []
            self._save_db()
            logger.info(f"Added new series to tracker: {series_name}")

    def remove_series(self, series_name: str):
        if series_name in self.db["tracked_series"]:
            del self.db["tracked_series"][series_name]
            self._save_db()
            logger.info(f"Removed series from tracker: {series_name}")

    def reset_db(self):
        """Clears the series database entirely."""
        self.db = {"tracked_series": {}}
        self._save_db()
        logger.info("Series database has been reset.")

    def get_tracked_series(self) -> List[str]:
        return list(self.db["tracked_series"].keys())

    def mark_downloaded(self, series_name: str, episode: float):
        if series_name in self.db["tracked_series"]:
            if episode not in self.db["tracked_series"][series_name]:
                self.db["tracked_series"][series_name].append(episode)
                self._save_db()
                logger.debug(f"Marked {series_name} - Ep {episode} as downloaded.")

    def is_downloaded(self, series_name: str, episode: float) -> bool:
        if series_name in self.db["tracked_series"]:
            return episode in self.db["tracked_series"][series_name]
        return False

    def parse_title(self, title: str) -> Optional[Tuple[str, str, float]]:
        """
        Parses a typical release title.
        Expected format: [Group] Series Name - Episode [Res]...
        Returns: (Group, Series_Name, Episode_Number) or None
        """
        # Regex explanation:
        # ^\[(.*?)\]            -> Group name in brackets at start
        # \s*(.*?)\s*           -> Series name (lazy)
        # -\s*(\d+(?:\.\d+)?)   -> Hyphen then Episode number
        # \s*(?:\[|\(|\s|$)     -> Followed by bracket, paren, space, or end of string
        
        pattern = r"^\[(.*?)\]\s*(.*?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:\[|\(|\s|$)"
        match = re.search(pattern, title)
        
        if match:
            group = match.group(1).strip()
            series = match.group(2).strip()
            episode = float(match.group(3))
            return group, series, episode
        return None

    def find_new_episodes(self, feed_items: List[Dict]) -> List[Dict]:
        """
        Scans RSS feed items, parses them, matches with tracked series,
        and returns items that are NEW (not downloaded).
        """
        new_items = []
        tracked = self.get_tracked_series()
        
        if not tracked:
            return new_items

        for item in feed_items:
            title = item.get('title', '')
            parsed = self.parse_title(title)
            if not parsed:
                continue
                
            group, parsed_series, episode = parsed
            
            # Check if group is in target groups
            group_str = f"[{group}]"
            is_target_group = any(g.lower() == group_str.lower() for g in Config.TARGET_GROUPS)
            if not is_target_group:
                continue
            
            # Check if it matches any tracked series
            matched_series = None
            for ts in tracked:
                if ts.lower() in parsed_series.lower():
                    matched_series = ts
                    break
                    
            if matched_series:
                if not self.is_downloaded(matched_series, episode):
                    item['matched_series'] = matched_series
                    item['episode'] = episode
                    new_items.append(item)
                    
        new_items = sorted(new_items, key=lambda x: (x['matched_series'], x['episode']))
        return new_items
