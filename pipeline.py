import os
import shutil
from core.logger import get_logger
from core.config import Config
from core.exceptions import NyaFinException, DownloadError, SubtitleExtractError
from modules.scraper import NyaaScraper
from modules.downloader import Downloader
from modules.media import MediaProcessor
from modules.translator import Translator

logger = get_logger(__name__)

class Pipeline:
    """Orchestrates the entire NyaFin automated process."""
    
    def __init__(self):
        self.scraper = NyaaScraper()
        self.downloader = Downloader()
        self.media = MediaProcessor()
        self.translator = Translator()
        from modules.tracker import Tracker
        self.tracker = Tracker()

    def run_auto(self):
        """Runs the pipeline automatically based on tracked series and RSS feed."""
        Config.STOP_EVENT.clear()
        logger.info("Starting automated pipeline run with series tracker...")
        
        try:
            items = self.scraper.fetch_latest()
            if not items:
                logger.info("No items found in RSS.")
                return

            new_episodes = self.tracker.find_new_episodes(items)
            
            if not new_episodes:
                logger.info("No new episodes found for tracked series.")
                return

            logger.info(f"Found {len(new_episodes)} new episode(s) to process.")
            
            for target in new_episodes:
                if Config.STOP_EVENT.is_set():
                    logger.warning("Pipeline stopped by user during auto run.")
                    break
                    
                series_name = target['matched_series']
                episode_num = target['episode']
                logger.info(f"Processing new episode: {series_name} - {episode_num}")
                
                try:
                    self.process_release(target['link'])  # Ensure we use 'link' which is torrent url in feedparser
                    # If successful, mark as downloaded
                    self.tracker.mark_downloaded(series_name, episode_num)
                except Exception as e:
                    logger.error(f"Failed to process {series_name} - {episode_num}: {e}")
            
        except NyaFinException as e:
            logger.error(f"Pipeline error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in pipeline: {e}")

    def run_manual(self, torrent_url: str):
        """Runs the pipeline for a manually provided URL."""
        Config.STOP_EVENT.clear()
        logger.info(f"Starting manual pipeline run for: {torrent_url}")
        try:
            self.process_release(torrent_url)
        except NyaFinException as e:
            logger.error(f"Pipeline error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in pipeline: {e}")

    def process_release(self, torrent_url: str):
        """Executes the core steps: Download -> Extract -> Translate -> Mux."""
        
        # Step 1: Download
        logger.info("--- Step 1: Downloading ---")
        torrent_hash = self.downloader.add_torrent(torrent_url)
        video_path = self.downloader.wait_for_completion(torrent_hash)
        
        if not video_path or not os.path.exists(video_path):
            raise DownloadError("Video file not found after download.")
            
        # Step 2: Extract Subtitles
        logger.info("--- Step 2: Extracting Subtitles ---")
        sub_index = self.media.find_english_subtitle_track(video_path)
        
        if sub_index is None:
            raise SubtitleExtractError("Hardsub veya altyazısız sürüm tespit edildi. İngilizce softsub yok.")
            
        eng_sub_path = self.media.extract_subtitle(video_path, sub_index, output_format="ass")
        
        # Step 3: Translate Subtitles
        logger.info("--- Step 3: Translating Subtitles ---")
        tr_sub_path = os.path.join(Config.TEMP_DIR, "TR_" + os.path.basename(eng_sub_path))
        self.translator.translate_subtitle_file(eng_sub_path, tr_sub_path)
        
        # Step 4: Mux Video
        logger.info("--- Step 4: Muxing Final Video ---")
        final_video_path = self.media.mux_video(video_path, tr_sub_path)
        
        # Step 5: Cleanup
        logger.info("--- Step 5: Cleanup ---")
        self._cleanup(eng_sub_path, tr_sub_path)
        
        logger.info(f"Pipeline completed successfully! Final video: {final_video_path}")

    def _cleanup(self, *files):
        """Removes temporary files."""
        for f in files:
            try:
                if os.path.exists(f):
                    os.remove(f)
                    logger.debug(f"Deleted temp file: {f}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {f}: {e}")
