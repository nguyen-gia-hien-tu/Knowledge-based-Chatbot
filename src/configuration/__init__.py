import logging
import os

from dotenv import load_dotenv

from configuration.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env file
load_dotenv(override=True)
settings = Settings()

# Create a file for the `GOOGLE_APPLICATION_CREDENTIALS` environment variable
# to point to for the Google Gemini API
with open("firebase-service-account.json", "w") as f:
    f.write(settings.FIREBASE_SERVICE_ACCOUNT)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "firebase-service-account.json"
