import logging

from dotenv import load_dotenv

from configuration.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env file
load_dotenv(override=True)
settings = Settings()

logger.info(settings)
