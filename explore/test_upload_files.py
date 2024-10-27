import mimetypes
import os
import shutil
from datetime import datetime
from functools import cmp_to_key
from pathlib import Path

import streamlit as st

################################################################################
# Set page configuration
################################################################################
st.set_page_config(
    page_title="Upload Files",
    page_icon=":open_file_folder:",
)

st.markdown(
    """
    <style>
    /* Apply CSS to all container divs to disable scroll */
    div[data-testid="stVerticalBlock"] > div {
        overflow: hidden; /* Disable scrolling */
        max-height: 100%; /* Ensure content doesn't overflow */
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
        margin-top: -7px !important;       /* Move the button up slightly */
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
        margin-top: -7px !important;       /* Move the button up slightly */
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
# Set page constants
################################################################################
DOCS_FOLDER = "documents"
CONTAINER_HEIGHT = 50


################################################################################
# Initialize session state variables
################################################################################
if "current_folder" not in st.session_state:
    st.session_state["current_folder"] = DOCS_FOLDER


################################################################################
# Utility functions
################################################################################
def truncate_filename(filename: str, length: int = 35) -> str:
    if len(filename) > length:
        return filename[: length - 10] + "..." + filename[-10:]
    return filename


def sort_folder_comparator(path_1: str, path_2: str) -> int:
    # Sort folders first, then files
    if os.path.isdir(path_1) and not os.path.isdir(path_2):
        return -1
    elif not os.path.isdir(path_1) and os.path.isdir(path_2):
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
    yes, no = st.columns(2)
    yes_clicked = yes.button("Yes", key="yes")
    no_clicked = no.button("No", key="no")

    if yes_clicked:
        if os.path.isdir(file_or_folder_path):
            shutil.rmtree(file_or_folder_path)
        else:
            os.remove(file_or_folder_path)

        st.session_state["current_folder"] = Path(
            st.session_state["current_folder"]
        ).parent
        st.rerun()
    elif no_clicked:
        st.rerun()


################################################################################
# Create upload file functionality
################################################################################
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    local_file = os.path.join(DOCS_FOLDER, uploaded_file.name)

    # Save the uploaded file to the local filesystem
    with open(local_file, "wb") as f:
        f.write(uploaded_file.getvalue())


################################################################################
# Start Main Feature
################################################################################
list_files_container = st.container(border=True)
list_files_container.markdown(f'#### {str(st.session_state["current_folder"])}')
list_files_container.divider()


######################################################################
# Write headers for listing available files and folders
######################################################################
cols = list_files_container.columns([0.5, 3, 1.5, 1, 1])

container = cols[0].container(height=CONTAINER_HEIGHT, border=False)
# container.checkbox("Select all", key="select_all", label_visibility="hidden")
delete_all_clicked = container.button(":x:", key="delete_all", type="primary")
if delete_all_clicked:
    delete_file_or_folder(st.session_state["current_folder"])

container = cols[1].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Name")

container = cols[2].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Type")

container = cols[3].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Size")

container = cols[4].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Time")


######################################################################
# Write entries for files and folders (non recursively)
######################################################################
current_folder = st.session_state["current_folder"]
files_and_folders_path = sorted(
    map(
        lambda filename: os.path.join(current_folder, filename),
        os.listdir(current_folder),
    ),
    key=cmp_to_key(sort_folder_comparator),
)
files_and_folders_name = map(
    lambda file_path: os.path.basename(file_path), files_and_folders_path
)

print("*" * 100)
print(f"Unsorted folder: {os.listdir(st.session_state['current_folder'])}")
print(f"Sorted folder: {files_and_folders_name}")
print("*" * 100)


######################################################################
# Add entry for "previous folder" to go back to the parent folder
######################################################################
container = cols[0].container(height=CONTAINER_HEIGHT, border=False)
# container.checkbox(
#     "File checkbox",
#     key=os.path.relpath(st.session_state["current_folder"]),
#     disabled=True,
#     label_visibility="hidden"
# )
container.button(
    ":heavy_minus_sign:",  # Disallow deleting the parent folder
    key=os.path.relpath(st.session_state["current_folder"]),
    disabled=True,
    type="primary",
)

container = cols[1].container(height=CONTAINER_HEIGHT, border=False)
previous_folder_clicked = container.button(
    label="..", use_container_width=True, type="primary"
)
if previous_folder_clicked:
    st.session_state["current_folder"] = Path(st.session_state["current_folder"]).parent
    # Re-run the script to list the files in the new folder instead of
    # continuing to list the files in the old folder
    st.rerun()

container = cols[2].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("Folder")

container = cols[3].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("N/A")

container = cols[4].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("N/A")


######################################################################
# Add entries for all files and folders (non recursively) in the current folder
######################################################################
for file_or_folder_name in files_and_folders_name:
    # Get the file path including the folder name
    file_path = os.path.join(st.session_state["current_folder"], file_or_folder_name)

    # Get the content type, file size, and upload time of file/folder
    if os.path.isdir(file_path):
        content_type = "Folder"
        file_size = "N/A"
        upload_time = "N/A"
    else:
        content_type, encoding = mimetypes.guess_type(file_path)
        file_size = "{:.2f} KB".format(os.path.getsize(file_path) / 1024)
        upload_time = datetime.fromtimestamp(os.path.getctime(file_path)).strftime(
            "%b %d, %Y"
        )

    # Create button to delete the file/folder
    container = cols[0].container(height=CONTAINER_HEIGHT, border=False)
    # container.checkbox(
    #     "File checkbox",
    #     value=st.session_state["select_all"],
    #     key=file_path,
    #     label_visibility="hidden"
    # )
    delete_clicked = container.button(":x:", key=file_path, type="primary")
    if delete_clicked:
        delete_file_or_folder(file_path)

    # Write the file/folder name
    container = cols[1].container(height=CONTAINER_HEIGHT, border=False)
    if os.path.isdir(file_path):
        folder_clicked = container.button(
            label=truncate_filename(file_or_folder_name),
            key=f"file_name_{file_path}",
            use_container_width=True,
            type="primary",
        )
        # If the folder is clicked, go to that folder
        if folder_clicked:
            st.session_state["current_folder"] = file_path
            print("*" * 100)
            print(f"Current folder: {st.session_state['current_folder']}")
            print("*" * 100)
            # Re-run the script to list the files in the new folder instead of
            # continuing to list the files in the old folder
            st.rerun()
    else:
        file_clicked = container.download_button(
            label=truncate_filename(file_or_folder_name),
            data=open(file_path, "rb").read(),
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

    container = cols[4].container(height=CONTAINER_HEIGHT, border=False)
    container.markdown(upload_time)
