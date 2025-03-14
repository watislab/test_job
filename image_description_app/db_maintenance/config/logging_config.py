import logging
import os
from dotenv import load_dotenv

load_dotenv()

def setup_logging():
    """Настраивает logging."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')

