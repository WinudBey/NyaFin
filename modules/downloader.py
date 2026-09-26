import time
import os
from typing import Optional
import qbittorrentapi
from core.logger import get_logger
from core.config import Config
from core.exceptions import DownloadError

logger = get_logger(__name__)

class Downloader:
    """Handles interaction with qBittorrent for downloading anime."""
    
    def __init__(self):
        self.host = Config.QB_HOST
        self.username = Config.QB_USER
        self.password = Config.QB_PASS
        self.client = None
        self._connect()

    def _connect(self):
        """Authenticates with the qBittorrent client."""
        logger.debug(f"Connecting to qBittorrent at {self.host}...")
        try:
            self.client = qbittorrentapi.Client(host=self.host, username=self.username, password=self.password)
            self.client.auth_log_in()
            logger.debug("Successfully authenticated with qBittorrent.")
        except qbittorrentapi.LoginFailed as e:
            logger.error(f"qBittorrent login failed: {e}")
            raise DownloadError(f"Login failed: {e}")
        except Exception as e:
            logger.error(f"qBittorrent connection error: {e}")
            raise DownloadError(f"Connection error: {e}")

    def add_torrent(self, torrent_url: str, save_path: str = Config.INPUT_DIR) -> str:
        """
        Adds a torrent URL or magnet link to qBittorrent.
        
        Args:
            torrent_url: URL to the .torrent file or magnet link.
            save_path: Directory where the file should be saved.
            
        Returns:
            The torrent hash.
        """
        if "nyaa.si/view/" in torrent_url:
            torrent_url = torrent_url.replace("nyaa.si/view/", "nyaa.si/download/") + ".torrent"
            logger.debug(f"Converted nyaa.si view link to download link: {torrent_url}")

        logger.debug(f"Adding torrent: {torrent_url} to {save_path}")
        try:
            # We must wait for the client to parse the torrent and return the hash.
            # qbittorrent-api returns "Ok." if successful.
            result = self.client.torrents_add(urls=torrent_url, save_path=save_path)
            
            # Since qBittorrent API might not return the hash immediately in `torrents_add`,
            # we fetch the latest added torrent.
            time.sleep(2) # Give it a brief moment to register
            torrents = self.client.torrents_info(sort='added_on', reverse=True)
            if not torrents:
                raise DownloadError("Failed to retrieve torrent info after adding.")
            
            # Assuming the most recently added is ours
            latest_torrent = torrents[0]
            logger.debug(f"Torrent added successfully. Hash: {latest_torrent.hash}, Name: {latest_torrent.name}")
            return latest_torrent.hash
        except Exception as e:
            logger.error(f"Failed to add torrent: {e}")
            raise DownloadError(f"Failed to add torrent: {e}")

    def wait_for_completion(self, torrent_hash: str, timeout: int = 3600, progress_callback: Optional[callable] = None) -> Optional[str]:
        """
        Polls the torrent status until it's 100% complete.
        
        Args:
            torrent_hash: Hash of the torrent to monitor.
            timeout: Maximum time in seconds to wait.
            progress_callback: Optional callback function(progress_percent, state_string)
            
        Returns:
            Absolute path to the downloaded video file.
        """
        logger.debug(f"Waiting for download completion (Hash: {torrent_hash})...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if Config.STOP_EVENT.is_set():
                logger.warning("Download cancelled by user.")
                raise DownloadError("Cancelled by user.")
                
            try:
                # We need a list to filter by hash
                torrents = self.client.torrents_info(torrent_hashes=torrent_hash)
                if not torrents:
                    raise DownloadError(f"Torrent {torrent_hash} not found in client.")
                
                torrent = torrents[0]
                progress = torrent.progress * 100
                logger.debug(f"Download Progress: {progress:.2f}%")
                
                if progress_callback:
                    # Provide localized status mapping if needed, or just use torrent.state
                    state_map = {
                        "downloading": "İndiriliyor...",
                        "stalledDL": "Bekliyor...",
                        "metaDL": "Meta veri indiriliyor...",
                        "checkingDL": "Kontrol ediliyor...",
                        "pausedDL": "Duraklatıldı",
                        "queuedDL": "Kuyrukta",
                        "allocating": "Yer ayrılıyor..."
                    }
                    detail_str = state_map.get(torrent.state, torrent.state)
                    progress_callback(progress, detail_str)
                
                if torrent.progress == 1.0 or torrent.state in ('uploading', 'stalledUP', 'pausedUP'):
                    logger.debug("Download complete.")
                    
                    # Use torrents_files to find the actual file path (works for both single file and directory)
                    files = self.client.torrents_files(torrent_hash)
                    if not files:
                        raise DownloadError(f"No files found for torrent {torrent_hash}")
                        
                    # Find the largest media file
                    save_path = torrent.save_path
                    video_file = max(files, key=lambda x: x.size)
                    full_path = os.path.join(save_path, video_file.name)
                        
                    logger.debug(f"Target video file: {full_path}")
                    return full_path
                    
            except Exception as e:
                logger.error(f"Error checking status: {e}")
                
            time.sleep(10) # Poll every 10 seconds
            
        logger.error("Download timed out.")
        raise DownloadError("Download timed out.")
