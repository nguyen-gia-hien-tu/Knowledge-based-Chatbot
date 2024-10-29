import logging
from pathlib import Path
from typing import Iterator

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


def get_blobs_in_folder_from_storage(
    folder_path: str = "",
    return_files: bool = True,
    return_folders: bool = True,
    recursive: bool = False,
) -> Iterator[Blob]:
    """
    Function to list files and folders from a folder in a Firebase Storage. If
    the folder_path is an empty string, return a list of all files and folders
    in the root directory.

    Args:
        folder_path (str): The folder path in the Firebase Storage. Defaults to `""`.
        return_files (bool): If True, return files. Defaults to `True`.
        return_folders (bool): If True, return folders. Defaults to `True`.
        recursive (bool): If True, list all files and folders recursively.
        Defaults to `False`.

    Returns:
        List[Blob]: Return a list of blobs (files and/or folders) in the given
            folder_path
    """
    bucket = storage.bucket()
    # If folder_path is empty, list all files in the root directory
    if folder_path == "":
        prefix = ""
    else:
        # Add "/" at the end to avoid mixing up with files of similar prefix
        prefix = folder_path.rstrip("/") + "/"

    blobs: Iterator[Blob] = bucket.list_blobs(prefix=prefix, delimiter="/")

    # Yield the files first (if return_files is True)
    if return_files:
        for blob in blobs:
            if not blob.name.endswith("/"):
                yield blob

    # Then, yield the folders (if return_folders is True)
    if return_folders:
        for prefix in blobs.prefixes:
            yield bucket.blob(prefix)

    # Finally, yield the files in the subfolders (if recursive is True)
    if recursive:
        for prefix in blobs.prefixes:
            yield from get_blobs_in_folder_from_storage(
                folder_path=prefix, recursive=True
            )


def create_folder_in_storage(folder_path: str):
    """Function to create a folder in Firebase Storage

    Args:
        folder_path (str): Path to the folder in Firebase Storage
    """
    bucket = storage.bucket()
    blob = bucket.blob(folder_path.rstrip("/") + "/")
    blob.upload_from_string("")


def upload_file_to_storage(uploaded_file: UploadedFile | Path, remote_path: str):
    """Function to upload file to Firebase Storage

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


def delete_blob_from_storage(remote_path: str):
    """Function to delete a file or folder from Firebase Storage

    Args:
        remote_path (str): Path to the file in Firebase Storage
    """
    bucket = storage.bucket()
    # If remote_path is a folder, delete all files in the folder
    if remote_path.endswith("/"):
        blobs: Iterator[Blob] = bucket.list_blobs(prefix=remote_path.rstrip("/") + "/")

        for blob in blobs:
            blob.delete()
    else:
        blob = bucket.blob(remote_path)
        blob.delete()
