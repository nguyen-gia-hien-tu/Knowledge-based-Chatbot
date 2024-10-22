from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Source code root directory (i.e., the path to the `src/` directory)
    SRC_ROOT: Path = Path(__file__).parent.parent

    # Path to the knowledge documents directory
    DOCUMENTS_DIR: Path = SRC_ROOT / "documents"

    GOOGLE_APPLICATION_CREDENTIALS: str
    FIREBASE_SERVICE_ACCOUNT_FILE: str
    FIREBASE_STORAGE_REMOTE_PATH: str
