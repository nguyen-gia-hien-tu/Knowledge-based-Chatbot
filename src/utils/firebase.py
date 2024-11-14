import base64
import json
import logging
import secrets
import string
from pathlib import Path
from typing import Dict, Iterator, Optional, Union

import firebase_admin
import requests
from firebase_admin import auth, credentials, storage
from firebase_admin.exceptions import FirebaseError
from google.cloud.storage import Blob
from google_auth_oauthlib import flow
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_oauth import OAuth2Component

from configuration import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


FIREBASE_AUTH_BASE_URL = "https://identitytoolkit.googleapis.com/v1/accounts:"


def initialize_firebase_app(firebase_service_account: Dict[str, str]):
    """
    Initialize the Firebase app

    Args:
        firebase_service_account (Dict[str, str]):
            The Firebase service account JSON object in dictionary format
    """

    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_service_account)
        firebase_admin.initialize_app(
            cred, {"storageBucket": settings.FIREBASE_STORAGE_BUCKET_NAME}
        )

        logging.info("*" * 100)
        logging.info(firebase_admin._apps)
        logging.info("*" * 100)


def create_new_user(email: str, password: str, name: str):
    """
    Create a new user with the given email, password, and name using Firebase
    https://firebase.google.com/docs/reference/admin/python/firebase_admin.auth#:~:text=SAML%20provider%20config.-,create_user,-(**kwargs

    Args:
        email (str): The email address of the user to be created
        password (str): The password of the user to be created
        name (str): The display name of the user to be created

    Returns:
        user (auth.UserRecord): The user information if the user is created

    Raises:
        e: Any error raised by Firebase
    """
    try:
        user: auth.UserRecord = auth.create_user(
            email=email, password=password, display_name=name
        )
        logger.info("*" * 100)
        logger.info(f"Successfully created user: {user.uid}")
        logger.info("*" * 100)
        return user
    except (ValueError, FirebaseError) as e:
        logger.info("*" * 100)
        logger.error(f"Error creating user: {e}")
        logger.info("*" * 100)
        raise e


def authenticate_user_with_password(
    email: str, password: str
) -> Optional[Dict[str, Union[str, bool]]]:
    """
    Authenticate a user with the given email and password using Firebase
    Authentication REST API
    https://firebase.google.com/docs/reference/rest/auth#section-sign-in-email-password

    Args:
        email (str):
            The email address of the user to be authenticated
        password (str):
            The password of the user to be authenticated

    Returns:
        Optional[Dict[str, Union[str, bool]]]:
            If there is an error, return None. Otherwise, return the JSON
            response containing the following:
                idToken (str):
                    A Firebase Auth ID token for the authenticated user.
                email (str):
                    The email for the authenticated user.
                refreshToken (str):
                    A Firebase Auth refresh token for the authenticated user.
                expiresIn (str):
                    The number of seconds in which the ID token expires.
                localId (str):
                    The uid of the authenticated user.
                registered (bool):
                    Whether the email is for an existing account.
    """
    url = f"{FIREBASE_AUTH_BASE_URL}signInWithPassword?key={settings.FIREBASE_API_KEY}"
    body = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    response = requests.post(url=url, json=body)
    if response.status_code != 200:
        logger.error("*" * 100)
        logger.error(f"Error authenticating user with password: {response.json()}")
        logger.error("*" * 100)
        return None

    return response.json()


def authenticate_user_with_google_oidc(
    auth_code: str,
    google_oidc_client_secret: Dict[str, str],
) -> auth.UserRecord:
    """
    Authenticate a user with Google OIDC using Google OAuth2.0 flow. If the user
    already has an account using the same email from the Firebase Authentication
    system, then we get the user info from Firebase. Otherwise, we create a new
    user in the Firebase.
    https://googleapis.github.io/google-api-python-client/docs/oauth.html

    Args:
        auth_code (str):
            The authentication code obtained when Google redirects back to the
            endpoint after the user signs in with Google
        google_oidc_client_secret (Dict[str, str]):
            The Google OIDC client secret JSON object

    Returns:
        auth.UserRecord:
            The user information from Firebase Authentication system
    """
    # Use authorization code to fetch token from Google
    google_flow = flow.Flow.from_client_config(
        google_oidc_client_secret,
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
        ],
    )
    google_flow.redirect_uri = settings.GOOGLE_OIDC_REDIRECT_URI
    google_flow.fetch_token(code=auth_code)

    # Obtain Google user info
    credentials = google_flow.credentials
    google_user = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"},
    ).json()

    # Firebase Authentication: Create a custom token
    firebase_token = auth.create_custom_token(google_user["sub"])

    # If the user already has an account using the same email, then we get the
    # user info from the Firebase Authentication system.
    firebase_user = get_user_by_email(google_user["email"])

    # Otherwise, although the user has signed in with Google, we still need
    # to create a new user in the Firebase Authentication system to be
    # compatible with the rest of the application.
    if firebase_user is None:

        # Generating a good password following the guidelines from
        # https://csguide.cs.princeton.edu/accounts/passwords
        alphabet = string.ascii_letters + string.digits
        generated_password = "".join(secrets.choice(alphabet) for _ in range(20))

        firebase_user = create_new_user(
            google_user["email"], generated_password, google_user["name"]
        )

    return firebase_user


def authenticate_user_with_google_using_streamlit_oauth(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> auth.UserRecord:
    """
    Authenticate a user with Google OIDC using the `streamlit-oauth` library. If
    the user already has an account using the same email from the Firebase
    Authentication, then we get the user info from Firebase. Otherwise, we
    create a new user in the Firebase.
    https://github.com/dnplus/streamlit-oauth/blob/main/examples/google.py

    Args:
        client_id (str):
            The Google OIDC client ID
        client_secret (str):
            The Google OIDC client secret
        redirect_uri (str):
            The redirect URI after the user signs in with Google

    Returns:
        auth.UserRecord:
            The user information from Firebase Authentication system
    """
    oauth2 = OAuth2Component(
        client_id,
        client_secret,
        "https://accounts.google.com/o/oauth2/v2/auth",
        "https://oauth2.googleapis.com/token",
        "https://oauth2.googleapis.com/token",
        "https://oauth2.googleapis.com/toketps://oauth2.googleapis.com/revoke",
    )

    result = oauth2.authorize_button(
        name="Sign in with Google",
        icon="https://www.google.com.tw/favicon.ico",
        redirect_uri=redirect_uri,
        scope="openid email profile",
        key="google",
        extras_params={"prompt": "consent", "access_type": "offline"},
        use_container_width=True,
        pkce="S256",
    )

    if result:
        # decode the id_token jwt and get the user's email address
        id_token: str = result["token"]["id_token"]
        # verify the signature is an optional step for security
        payload = id_token.split(".")[1]
        # add padding to the payload if needed
        payload += "=" * (-len(payload) % 4)
        # Load the payload into a dict representing user info
        google_user = json.loads(base64.b64decode(payload))

        # If the user already has an account using the same email, then we get the
        # user info from the Firebase Authentication system.
        firebase_user = get_user_by_email(google_user["email"])

        # Otherwise, although the user has signed in with Google, we still need
        # to create a new user in the Firebase Authentication system to be
        # compatible with the rest of the application.
        if firebase_user is None:

            # Generating a good password following the guidelines from
            # https://csguide.cs.princeton.edu/accounts/passwords
            alphabet = string.ascii_letters + string.digits + string.punctuation
            generated_password = "".join(secrets.choice(alphabet) for _ in range(20))

            logger.info("*" * 100)
            logger.info(f"Generated password: {generated_password}")
            logger.info("*" * 100)

            firebase_user = create_new_user(
                google_user["email"], generated_password, google_user["name"]
            )

        return firebase_user


def get_user_by_token(id_token: str) -> Optional[auth.UserRecord]:
    """
    Function to get the user information from the JWT token if the token is
    valid. Otherwise, return None.

    Verify the JWT token:
    https://firebase.google.com/docs/reference/admin/python/firebase_admin.auth#:~:text=the%20user%20account.-,verify_id_token

    Get the user information:
    https://firebase.google.com/docs/reference/admin/python/firebase_admin.auth#:~:text=the%20SAML%20provider.-,get_user,-(uid)

    Args:
        id_token (str): The JWT token presenting the user

    Returns:
        auth.UserRecord:
            The user's information if the token is valid, otherwise None
            https://firebase.google.com/docs/reference/admin/python/firebase_admin.auth#firebase_admin.auth.UserRecord:~:text=class%20firebase_admin.auth.UserRecord(data)
    """
    try:
        decoded_token = auth.verify_id_token(id_token=id_token, clock_skew_seconds=5)
        user = auth.get_user(decoded_token["uid"])
    except Exception as e:
        logger.error("*" * 100)
        logger.error(f"Error getting user from token: {e}")
        logger.error("*" * 100)
        return None

    return user


def get_user_by_email(email: str) -> Optional[auth.UserRecord]:
    """
    Function to get the user information from the email address
    https://firebase.google.com/docs/reference/admin/python/firebase_admin.auth#:~:text=retrieving%20the%20user.-,get_user_by_email,-(email)

    Args:
        email (str):
            The email address of the user

    Returns:
        Optional[auth.UserRecord]:
            The user information of the user with the given email address in
            Firebase. If the user does not exist, return None.
    """
    try:
        user: auth.UserRecord = auth.get_user_by_email(email)
    except Exception as e:
        logger.error("*" * 100)
        logger.error(f"Error getting user by email in Firebase: {e}")
        logger.error("*" * 100)
        return None

    return user


def update_user_info_by_email(email: str, **kwargs) -> auth.UserRecord:
    """
    Function to update the user information of the user with the given email
    https://firebase.google.com/docs/reference/admin/python/firebase_admin.auth#:~:text=SAML%20provider%20config.-,update_user,-(uid%2C

    Args:
        email (str):
            The email address of the user to be updated

    Returns:
        auth.UserRecord:
            The updated user information if the user exists. Otherwise, return
            None
    """
    try:
        user = get_user_by_email(email)
        if user:
            updated_user = auth.update_user(user.uid, **kwargs)
        else:
            logger.error("*" * 100)
            logger.error(f"User with email {email} does not exist.")
            logger.error("*" * 100)
            return None
    except Exception as e:
        logger.error("*" * 100)
        logger.error(f"Error updating user info: {e}")
        logger.error("*" * 100)
        return None

    return updated_user


def reset_password(email: str):
    """
    Function to send a password reset email to the given email address using
    Firebase Authentication REST API
    https://firebase.google.com/docs/reference/rest/auth#section-send-password-reset-email

    Args:
        email (str):
            The email address to send the password reset email to
    """
    url = f"{FIREBASE_AUTH_BASE_URL}sendOobCode?key={settings.FIREBASE_API_KEY}"
    body = {
        "requestType": "PASSWORD_RESET",
        "email": email,
    }
    response = requests.post(url=url, json=body)
    if response.status_code != 200:
        logger.error(f"Error sending password reset email: {response.json()}")

    return


def delete_user_by_uid(uid: str):
    """
    Function to delete a user from Firebase Authentication using the user's UID

    Args:
        uid (str):
            The UID of the user to be deleted

    Returns:
        uid (str):
            The UID of the user that is deleted. If an error occurs, return None
    """
    try:
        auth.delete_user(uid)
    except Exception as e:
        logger.error("*" * 100)
        logger.error(f"Error deleting user: {e}")
        logger.error("*" * 100)
        return None

    return uid


def get_file_from_storage(remote_path: str) -> Blob:
    """
    Function to get a file from Firebase Storage
    https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.bucket.Bucket#google_cloud_storage_bucket_Bucket_blob

    Args:
        remote_path (str):
            Path to the file in Firebase Storage

    Returns:
        Blob:
            If the file exists in the given remote_path, return the download URL
            of the file. Otherwise, return None.
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
    Function to list files and folders from a given folder in Firebase Storage.
    If the given folder_path is an empty string, return a list of all files and
    folders in the root directory.

    Args:
        folder_path (str):
            The folder path in the Firebase Storage. Defaults to `""`.
        return_files (bool):
            If True, include files in the returned list. Defaults to `True`.
        return_folders (bool):
            If True, include folders in the returned list. Defaults to `True`.
        recursive (bool):
            If True, list all files and folders recursively. Defaults to
            `False`.

    Returns:
        Iterator[Blob]:
            Return an iterator of blobs (files and/or folders) in the given
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
                folder_path=prefix,
                return_files=return_files,
                return_folders=return_folders,
                recursive=True,
            )


def create_folder_in_storage(folder_path: str):
    """
    Function to create a folder in Firebase Storage

    Args:
        folder_path (str): Path to the folder in Firebase Storage
    """
    bucket = storage.bucket()
    blob = bucket.blob(folder_path.rstrip("/") + "/")
    blob.upload_from_string("")


def upload_file_to_storage(uploaded_file: UploadedFile | Path, remote_path: str):
    """
    Function to upload file to Firebase Storage

    Args:
        uploaded_file (UploadedFile):
            File to be uploaded from Streamlit app
        remote_path (str):
            Path to the location in Firebase Storage to store the file
    """
    bucket = storage.bucket()
    blob = bucket.blob(remote_path)
    if isinstance(uploaded_file, UploadedFile):
        blob.upload_from_file(uploaded_file, content_type=uploaded_file.type)
    else:
        blob.upload_from_filename(uploaded_file)


def delete_blob_from_storage(remote_path: str):
    """
    Function to delete a file or folder from Firebase Storage
    https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.blob.Blob#google_cloud_storage_blob_Blob_delete

    Args:
        remote_path (str):
            Path to the file or folder in Firebase Storage
    """
    bucket = storage.bucket()
    blobs: Iterator[Blob] = bucket.list_blobs(prefix=remote_path)

    for blob in blobs:
        blob.delete()
