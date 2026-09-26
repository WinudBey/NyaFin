import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Setup directories
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Clear the log file on each start to prevent unlimited growth during dev, as requested by the user
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        f.truncate()

def get_logger(name: str) -> logging.Logger:
    """
    Creates and configures a standard logger for the application.
    Logs DEBUG level both to console and the app.log file.
    
    Args:
        name: Name of the module requesting the logger.
        
    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # To avoid duplicate logs if get_logger is called multiple times for the same module
    if not logger.handlers:
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        # File Handler (Rotating)
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=10*1024*1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
