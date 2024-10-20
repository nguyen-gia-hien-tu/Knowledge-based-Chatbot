import firebase_admin
from firebase_admin import credentials, storage

from configuration import settings


def initialize_firebase_app():
    """Function to initialize firebase connection"""

    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_FILE)
        firebase_admin.initialize_app(
            cred, {"storageBucket": settings.FIREBASE_STORAGE_REMOTE_PATH}
        )
