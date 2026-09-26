import os
import threading
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Centralized configuration class for the application."""
    
    # Base paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    TEMP_DIR = os.path.join(DATA_DIR, "temp")
    INPUT_DIR = os.path.join(DATA_DIR, "input")
    OUTPUT_DIR = os.path.join(DATA_DIR, "output")
    
    # RSS Configuration
    NYAA_RSS_URL = os.getenv("NYAA_RSS_URL", "https://nyaa.si/?page=rss&q=1080p&c=1_2&f=0")
    TARGET_GROUPS = os.getenv("TARGET_GROUPS", "[SubsPlease],[Erai-raws]").split(",")
    
    # qBittorrent Configuration
    QB_HOST = os.getenv("QB_HOST", "http://localhost:8080")
    QB_USER = os.getenv("QB_USER", "admin")
    QB_PASS = os.getenv("QB_PASS", "adminadmin")
    
    # LLM (Ollama) Configuration
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    
    # Translation & Execution Control
    TRANSLATOR_PRIMARY_SERVICE = os.getenv("TRANSLATOR_PRIMARY_SERVICE", "bing")
    STOP_EVENT = threading.Event()
    
    @classmethod
    def ensure_dirs(cls):
        """Ensures all necessary data directories exist."""
        for d in [cls.DATA_DIR, cls.TEMP_DIR, cls.INPUT_DIR, cls.OUTPUT_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)

# Initialize directories on load
Config.ensure_dirs()

