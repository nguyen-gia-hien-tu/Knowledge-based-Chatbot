from datetime import datetime
import mimetypes
import os
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
    </style>
    """,
    unsafe_allow_html=True
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
        return filename[:length-10] + "..." + filename[-10:]
    return filename


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
current_folder: str = str(st.session_state["current_folder"])
list_files_container.markdown(f'#### {current_folder}')
list_files_container.divider()


############################################################
# Write headers for listing available files and folders
############################################################
cols = list_files_container.columns([0.5, 3, 1.5, 1, 1])

container = cols[0].container(height=CONTAINER_HEIGHT, border=False)
container.checkbox("Select all", key="select_all", label_visibility="hidden")

container = cols[1].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Name")

container = cols[2].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Type")

container = cols[3].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Size")

container = cols[4].container(height=CONTAINER_HEIGHT, border=False)
container.markdown("##### Time")


############################################################
# Write entries for files and folders (non recursively)
############################################################
files_and_folders = os.listdir(st.session_state["current_folder"])

print("*" * 100)
print(files_and_folders)
print("*" * 100)


############################################################
# Add entry for "previous folder" to go back to the parent folder
############################################################
container = cols[0].container(height=CONTAINER_HEIGHT, border=False)
container.checkbox(
    "File checkbox",
    key=os.path.relpath(st.session_state["current_folder"]),
    label_visibility="hidden"
)

container = cols[1].container(height=CONTAINER_HEIGHT, border=False)
previous_folder_clicked = container.button(
    label="..",
    use_container_width=True,
    type="primary"
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


############################################################
# Add entries for all files and folders (non recursively) in the current folder
############################################################
for file_or_folder in files_and_folders:
    # Get the file path including the folder name
    file_path = os.path.join(st.session_state["current_folder"], file_or_folder)

    # Get the content type, file size, and upload time of file/folder
    if os.path.isdir(file_path):
        content_type = "Folder"
        file_size = "N/A"
        upload_time = "N/A"
    else:
        content_type, encoding = mimetypes.guess_type(file_path)
        file_size = "{:.2f} KB".format(os.path.getsize(file_path) / 1024)
        upload_time = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%b %d, %Y")

    # Create checkbox to select the file/folder
    container = cols[0].container(height=CONTAINER_HEIGHT, border=False)
    container.checkbox(
        "File checkbox",
        value=st.session_state["select_all"],
        key=file_path,
        label_visibility="hidden"
    )

    # Write the file/folder name
    container = cols[1].container(height=CONTAINER_HEIGHT, border=False)
    file_or_folder_clicked = container.button(
        label=truncate_filename(file_or_folder),
        key=f"file_name_{file_path}",
        use_container_width=True,
        type="primary"
    )
    if file_or_folder_clicked:
        if os.path.isdir(file_path):
            st.session_state["current_folder"] = file_path
            print("*" * 100)
            print(f"Current folder: {st.session_state['current_folder']}")
            print("*" * 100)
            # Re-run the script to list the files in the new folder instead of
            # continuing to list the files in the old folder
            st.rerun()

    # Write the content type
    container = cols[2].container(height=CONTAINER_HEIGHT, border=False)
    container.markdown(content_type)

    # Write the file size or N/A for folder
    container = cols[3].container(height=CONTAINER_HEIGHT, border=False)
    container.markdown(file_size)

    container = cols[4].container(height=CONTAINER_HEIGHT, border=False)
    container.markdown(upload_time)

