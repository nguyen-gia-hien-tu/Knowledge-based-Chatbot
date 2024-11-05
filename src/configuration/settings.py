from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Source code root directory (i.e., the path to the `src/` directory)
    SRC_ROOT: Path = Path(__file__).parent.parent

    # Settings for Single Sign-On (SSO) with Google
    GOOGLE_OIDC_CLIENT_SECRET_FILE: str
    GOOGLE_OIDC_REDIRECT_URI: str = "http://localhost:8080"

    # Path to the knowledge documents directory
    DOCUMENTS_DIR: str = "documents/"
    # Vector database index name
    VECTOR_DB_INDEX_NAME: str = "knowledge-based-chatbot-index"
    # Record manager database URL
    RECORD_MANAGER_DB_URL: str = "sqlite:///record_manager_cache.db"

    # Firebase settings
    FIREBASE_API_KEY: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    FIREBASE_SERVICE_ACCOUNT_FILE: str
    FIREBASE_STORAGE_BUCKET_NAME: str
