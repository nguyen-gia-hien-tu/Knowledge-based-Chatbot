import logging
import mimetypes
from functools import cmp_to_key
from pathlib import PurePosixPath
from typing import List

import streamlit as st
from google.cloud.storage import Blob

from utils.firebase import (
    create_folder_in_storage,
    delete_blob_from_storage,
    get_blobs_in_folder_from_storage,
    get_file_from_storage,
    upload_file_to_storage,
)
from utils.rag import setup_embedding, setup_pinecone_index, setup_retriever

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def setup_fresh_retriever():
    """Set up a fresh retriever by clearing the cache and calling the function again

    Args:
        _index (_type_): _description_
        _embedding (_type_): _description_
    """
    logger.info("*" * 100)
    logger.info("Setting up a fresh retriever")

    # Get the Pinecone index and the embedding model
    index = setup_pinecone_index()
    embedding = setup_embedding()

    # Clear the cache on the setup_retriever() function to let it run again
    setup_retriever.clear()
    setup_retriever(index, embedding, st.session_state["uid"], st.session_state["uid"])

    logger.info("*" * 100)
    logger.info("Retriever is refreshed")
    logger.info("*" * 100)


def initialize_session_state():
    """Initialize the session state for the page"""

    if "current_folder" not in st.session_state:
        # If the user does not have a folder in Firebase Storage, create one
        # using the user's UID
        if not get_file_from_storage(st.session_state["uid"]):
            create_folder_in_storage(st.session_state["uid"])

        st.session_state["current_folder"] = st.session_state["uid"]


def setup_css():
    """Set up the CSS for the page"""

    st.markdown(
        """
        <style>
        /* Apply CSS to all container divs to disable scroll */
        div[data-testid="stVerticalBlock"] > div {
            overflow: hidden;       /* Disable scrolling */
            max-height: 100%;       /* Ensure content doesn't overflow */
        }

        /* Apply CSS to button of type "primary" */
        /* https://discuss.streamlit.io/t/how-to-get-click-action-in-a-text/39441/4 */
        button[kind="primary"] {
            background: none!important;
            border: none;
            color: light-dark(black, white) !important;     /* Dynamically set text color contrast to the theme */
            text-decoration: none;
            cursor: pointer;
            border: none !important;
            display: flex;                      /* Make button content flexible */
            justify-content: flex-start;        /* Align button content to the left */
            margin-top: -7px !important;        /* Move the button up slightly */
            padding: 0px 0px !important;        /* Adjust padding if necessary */
        }
        button[kind="primary"]:hover {
            text-decoration: none;
            color: light-dark(blue, cyan) !important;
        }

        download_button[kind="primary"] {
            background: none!important;
            border: none;
            color: light-dark(black, white) !important;     /* Dynamically set text color contrast to the theme */
            text-decoration: none;
            cursor: pointer;
            border: none !important;
            display: flex;                      /* Make button content flexible */
            justify-content: flex-start;        /* Align button content to the left */
            margin-top: -7px !important;        /* Move the button up slightly */
            padding: 0px 0px !important;        /* Adjust padding if necessary */
        }
        download_button[kind="primary"]:hover {
            text-decoration: none;
            color: light-dark(blue, cyan) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


################################################################################
# Utility functions
################################################################################
def truncate_filename(filename: str, length: int = 30) -> str:
    if len(filename) > length:
        return filename[: length - 10] + "..." + filename[-10:]
    return filename


def sort_blob_comparator(blob_1: Blob, blob_2: Blob) -> int:
    path_1: str = blob_1.name
    path_2: str = blob_2.name

    # Sort folders first, then files
    if path_1.endswith("/") and not path_2.endswith("/"):
        return -1
    elif not path_1.endswith("/") and path_2.endswith("/"):
        return 1
    else:
        # Sort by name if both are folders or both are files
        if path_1 < path_2:
            return -1
        elif path_1 > path_2:
            return 1
        else:
            return 0


@st.dialog("⚠ DELETE file or folder ⚠")
def delete_file_or_folder(file_or_folder_path: str):
    st.write("Are you sure you want to delete this file or folder?")
    _, no, yes = st.columns([5, 1, 1])
    no_clicked = no.button("No", key="no", use_container_width=True)
    yes_clicked = yes.button("Yes", key="yes", use_container_width=True)

    if no_clicked:
        st.rerun()
    elif yes_clicked:
        # Folders in Firebase Storage end with "/"
        # If the to-be-deleted folder is the current folder, go back to the
        # parent folder
        if (
            file_or_folder_path.endswith("/")
            and st.session_state["current_folder"] == file_or_folder_path
        ):
            st.session_state["current_folder"] = (
                str(PurePosixPath(st.session_state["current_folder"]).parent) + "/"
            )

        delete_blob_from_storage(file_or_folder_path)
        setup_fresh_retriever()

        st.rerun()


@st.dialog("Create New Folder")
def create_new_folder():
    st.write("Enter the name of the new folder:")
    new_folder_name = st.text_input("New Folder Name", key="new_folder_name")

    _, cancel, create = st.columns([3, 1, 1])
    cancel_clicked = cancel.button("Cancel", key="cancel", use_container_width=True)
    create_clicked = create.button("Create", key="create", use_container_width=True)

    if cancel_clicked:
        st.rerun()
    elif create_clicked:
        new_folder_path = str(
            PurePosixPath(st.session_state["current_folder"]).joinpath(new_folder_name)
        )
        create_folder_in_storage(new_folder_path)
        st.rerun()


################################################################################
# Main function
################################################################################

######################################################################
# Set the page configuration
######################################################################
# Page title
st.title("Upload Documents")
# Set up the CSS for the page
setup_css()
# Initialize the session state for the page
initialize_session_state()
# Constants
CONTAINER_HEIGHT = 50

######################################################################
# Create file upload section
######################################################################

# With only the "file_uploader" widget, after uploading a file, there will be
# another widget appearing below the "file_uploader" widget, showing what the
# uploaded file is. This causes the file to be automatically uploaded again
# after the user clicks the delete button to delete the file. Use the "form"
# feature to clear the widget after submission
# https://discuss.streamlit.io/t/clear-the-cache-for-file-uploder-on-streamlit/14304/2

file_upload_form = st.form("file_upload_form", clear_on_submit=True)
uploaded_file = file_upload_form.file_uploader("Upload a PDF File", type="pdf")
submitted = file_upload_form.form_submit_button("Upload :rocket:")

# If the upload button is clicked and a file is selected
if submitted and uploaded_file:
    # Upload file to Firebase Storage
    remote_path = str(
        PurePosixPath(st.session_state["current_folder"]).joinpath(uploaded_file.name)
    )
    upload_file_to_storage(uploaded_file, remote_path)
    success_banner = st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Restart the retriever to include the new file
    try:
        setup_fresh_retriever()
        logger.info("*" * 100)
        logger.info(f"File '{uploaded_file.name}' uploaded to Firebase")
        logger.info("*" * 100)
    except Exception as e:
        logger.info("*" * 100)
        logger.error(f"Error setting up retriever while uploading file: {e}")
        logger.info("*" * 100)

        remote_path = str(
            PurePosixPath(st.session_state["uid"]).joinpath(uploaded_file.name)
        )
        delete_blob_from_storage(remote_path)

    # Clear the success message
    success_banner.empty()

######################################################################
# Write the current folder path
######################################################################
list_files_container = st.container(border=True)

# TODO: Display the current folder path without the user ID for better readability
# current_folder_path_without_uid = str(
#     PurePosixPath(st.session_state["current_folder"]).relative_to(
#         st.session_state["uid"]
#     )
# )

display_current_folder = list_files_container.container(border=False)
display_current_folder.markdown(f'#### {str(st.session_state["current_folder"])}')

# Add a button to refresh the page
refresh_container = list_files_container.container(border=False)
if refresh_container.button(
    "Refresh", icon=":material/refresh:", use_container_width=True
):
    st.rerun()

# Add a button to create a new folder
create_new_folder_container = list_files_container.container(border=False)
if create_new_folder_container.button(
    label="Create New Folder",
    icon=":material/create_new_folder:",
    use_container_width=True,
):
    create_new_folder()

list_files_container.divider()

######################################################################
# Get all files and folders in the current folder
######################################################################
# Sort the files and folders in the order of "folder" type first and in
# lexicographical order if objects are of the same type
files_and_folders_blobs: List[Blob] = sorted(
    get_blobs_in_folder_from_storage(st.session_state["current_folder"]),
    key=cmp_to_key(sort_blob_comparator),
)

logger.info("*" * 100)
logger.info(f"Files and folders in \"{st.session_state['current_folder']}\":")
logger.info([blob.name for blob in files_and_folders_blobs])
logger.info("*" * 100)

######################################################################
# Write headers for listing available files and folders
######################################################################
cols = list_files_container.columns([0.5, 3, 1.5, 1, 1.2])

# Add a button to delete all files and folders in the current folder
container = cols[0].container(height=CONTAINER_HEIGHT, border=False)
# container.checkbox("Select all", key="select_all", label_visibility="hidden")
delete_all_clicked = container.button(
    ":x:",
    key="delete_all",
    disabled=st.session_state["current_folder"] == st.session_state["uid"],
    type="primary",
)
if delete_all_clicked:
    delete_file_or_folder(st.session_state["current_folder"])

# Add headers for Name, Type, Size, and Time columns
container = cols[1].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Name")

container = cols[2].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Type")

container = cols[3].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Size")

container = cols[4].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Time")

######################################################################
# Add entry for "previous folder" to go back to the parent folder
######################################################################
# Create a disabled button to disallow deleting the parent folder
container = cols[0].container(height=CONTAINER_HEIGHT, border=False)
container.button(
    ":heavy_minus_sign:",  # Disallow deleting the parent folder
    disabled=True,
    type="primary",
)

# Create a button to go back to the parent folder
container = cols[1].container(height=CONTAINER_HEIGHT, border=False)
previous_folder_clicked = container.button(
    label="../",
    icon=":material/folder_open:",
    use_container_width=True,
    disabled=st.session_state["current_folder"] == st.session_state["uid"],
    type="primary",
)
if previous_folder_clicked:
    st.session_state["current_folder"] = (
        str(PurePosixPath(st.session_state["current_folder"]).parent) + "/"
    )
    # Re-run the script to list the files in the new folder instead of
    # continuing to list the files in the old folder
    st.rerun()

# Add values for the "Type", "Size", and "Time" columns
container = cols[2].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("Folder")

container = cols[3].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("N/A")

container = cols[4].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("N/A")

######################################################################
# Add entries for all files and folders (non recursively)
# in the current folder
######################################################################
for file_or_folder_blob in files_and_folders_blobs:
    # Get the file/folder full path and only name
    file_or_folder_path: str = file_or_folder_blob.name
    file_or_folder_name: str = PurePosixPath(file_or_folder_path).name

    # Get the content type, file size, and upload time of file/folder
    # Folders in Firebase Storage end with "/"
    if file_or_folder_path.endswith("/"):
        content_type = "Folder"
        file_size = "N/A"
        upload_time = "N/A"
    else:
        content_type, encoding = mimetypes.guess_type(file_or_folder_name)
        file_size = "{:.2f} KB".format(file_or_folder_blob.size / 1024)
        upload_time = file_or_folder_blob.time_created.strftime("%b %d, %Y")

    # Create button to delete the file/folder
    container = cols[0].container(height=CONTAINER_HEIGHT, border=False)
    delete_clicked = container.button(":x:", key=file_or_folder_path, type="primary")
    if delete_clicked:
        delete_file_or_folder(file_or_folder_path)
        logger.info("*" * 100)
        logger.info(f"File/Folder '{file_or_folder_path}' deleted")
        logger.info("*" * 100)

    # Write the file/folder name
    container = cols[1].container(height=CONTAINER_HEIGHT, border=False)
    # Folders in Firebase Storage end with "/"
    if file_or_folder_path.endswith("/"):
        # Create a button desgined for folders
        folder_clicked = container.button(
            label=f"{truncate_filename(file_or_folder_name)}",
            help=file_or_folder_name,
            icon=":material/folder:",
            use_container_width=True,
            type="primary",
        )
        # If the folder is clicked, go to that folder
        if folder_clicked:
            st.session_state["current_folder"] = file_or_folder_path
            # Re-run the script to list the files in the new folder instead of
            # continuing to list the files in the old folder
            st.rerun()
    else:
        # Create a button to download the file
        container.download_button(
            label=f"{truncate_filename(file_or_folder_name)}",
            help=file_or_folder_name,
            icon=":material/picture_as_pdf:",
            data=file_or_folder_blob.download_as_bytes(),
            file_name=file_or_folder_name,
            mime=content_type,
            type="primary",
        )

    # Write the content type
    container = cols[2].container(height=CONTAINER_HEIGHT, border=False)
    container.markdown(content_type)

    # Write the file size or N/A for folder
    container = cols[3].container(height=CONTAINER_HEIGHT, border=False)
    container.markdown(file_size)

    # Write the upload time
    container = cols[4].container(height=CONTAINER_HEIGHT, border=False)
    container.markdown(upload_time)
