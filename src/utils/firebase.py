import logging
from pathlib import Path
from typing import List

import firebase_admin
from firebase_admin import credentials, storage
from google.cloud.storage import Blob
from streamlit.runtime.uploaded_file_manager import UploadedFile

from configuration import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_firebase_app():
    """Function to initialize Firebase connection"""

    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_FILE)
        firebase_admin.initialize_app(
            cred, {"storageBucket": settings.FIREBASE_STORAGE_BUCKET_NAME}
        )

        logging.info("*" * 100)
        logging.info(firebase_admin._apps)
        logging.info("*" * 100)


def get_file_from_storage(remote_path: str) -> Blob:
    """Function to get a file from Firebase Storage

    Args:
        remote_path (str): Path to the file in Firebase Storage

    Returns:
        Blob: if the file exists in the given remote_path, return the download
            URL of the file. Otherwise, return None.
    """
    bucket = storage.bucket()
    blob = bucket.blob(remote_path)

    return blob if blob.exists() else None


def get_files_in_folder_from_storage(folder_path: str = "") -> List[Blob]:
    """Function to recursively list files from a folder in a Firebase Storage.
    This function only list file names and not the folder or subfolder names.

    Args:
        folder_path (str): The folder path in the Firebase Storage

    Returns:
        List[Blob]: if the files exist in the given folder_path, return a list
            of download URLs of the files. Otherwise, return an empty list. If
            the folder_path is an empty string, return a list of all files in
            the root directory.
    """
    bucket = storage.bucket()
    if folder_path == "":
        prefix = ""
    else:
        prefix = folder_path if folder_path.endswith("/") else folder_path + "/"

    blobs: List[Blob] = bucket.list_blobs(prefix=prefix)

    return [blob for blob in blobs if not blob.name.endswith("/")]


def upload_file_to_storage(uploaded_file: UploadedFile | Path, remote_path: str):
    """Function to upload file to a folder in Firebase Storage

    Args:
        uploaded_file (UploadedFile): File to be uploaded from Streamlit app
        remote_path (str): Path to the location in Firebase Storage for the file
    """
    bucket = storage.bucket()
    blob = bucket.blob(remote_path)
    if isinstance(uploaded_file, UploadedFile):
        blob.upload_from_file(uploaded_file, content_type=uploaded_file.type)
    else:
        blob.upload_from_filename(uploaded_file)


def delete_file_from_storage(remote_path: str):
    """Function to delete a file from Firebase Storage

    Args:
        remote_path (str): Path to the file in Firebase Storage
    """
    bucket = storage.bucket()
    blob = bucket.blob(remote_path)
    blob.delete()
