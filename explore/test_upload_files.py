from datetime import datetime
import mimetypes
import os
import streamlit as st


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
    button[kind="primary"] {
        background: none!important;
        border: none;
        color: black !important;
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
        color: blue !important;
    }
    button[kind="primary"]:focus {
        outline: none !important;
        box-shadow: none !important;
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def truncate_filename(filename: str, length: int = 35) -> str:
    if len(filename) > length:
        return filename[:length-10] + "..." + filename[-10:]
    return filename


################################################################################
# Create upload file functionality
################################################################################
DOCS_FOLDER = "documents"

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    local_file = os.path.join(DOCS_FOLDER, uploaded_file.name)

    # Save the uploaded file to the local filesystem
    with open(local_file, "wb") as f:
        f.write(uploaded_file.getvalue())


if "current_folder" not in st.session_state:
    st.session_state["current_folder"] = DOCS_FOLDER

st.subheader(st.session_state["current_folder"])


################################################################################
# Write headers for listing available files and folders
################################################################################
CONTAINER_HEIGHT = 50
cols = st.columns([0.5, 3, 1.5, 1, 1])

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



################################################################################
# List all files and folders
################################################################################
files_and_folders = os.listdir(st.session_state["current_folder"])

print("*" * 100)
print(files_and_folders)
print("*" * 100)

for file_or_folder in files_and_folders:
    file_path = os.path.join(st.session_state["current_folder"], file_or_folder)

    if os.path.isdir(file_path):
        content_type = "Folder"
        file_size = "N/A"
        upload_time = "N/A"
    else:
        content_type, encoding = mimetypes.guess_type(file_path)
        file_size = "{:.2f} KB".format(os.path.getsize(file_path) / 1024)
        upload_time = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%b %d, %Y")

    # Create checkbox for the file/folder
    container = cols[0].container(height=CONTAINER_HEIGHT, border=False)
    container.checkbox(
        "File checkbox",
        value=st.session_state["select_all"],
        key=file_path,
        label_visibility="hidden"
    )

    # Write the file/folder name
    container = cols[1].container(height=CONTAINER_HEIGHT, border=False)
    # container.markdown(truncate_filename(file_or_folder))
    container.button(
        label=truncate_filename(file_or_folder),
        key=f"file_name_{file_path}",
        use_container_width=True,
        type="primary"
    )

    # Write the content type
    container = cols[2].container(height=CONTAINER_HEIGHT, border=False)
    container.markdown(content_type)

    # Write the file size or N/A for folder
    container = cols[3].container(height=CONTAINER_HEIGHT, border=False)
    container.markdown(file_size)

    container = cols[4].container(height=CONTAINER_HEIGHT, border=False)
    container.markdown(upload_time)

