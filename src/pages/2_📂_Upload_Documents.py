import logging
import os
import tempfile
from pathlib import Path
from typing import List

import streamlit as st
from google.cloud.storage import Blob
from streamlit.runtime.uploaded_file_manager import UploadedFile

from configuration import settings
from utils.firebase import (
    delete_file_from_storage,
    get_files_in_folder_from_storage,
    upload_file_to_storage,
)
from utils.utils import setup_embedding, setup_pinecone_index, setup_retriever

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def main():

    # Function to perform when the user uploads a file
    def upload_file(uploaded_file: UploadedFile | Path, remote_path: str = None):
        if remote_path is None:
            remote_path = os.path.join(settings.DOCUMENTS_DIR, uploaded_file.name)
        upload_file_to_storage(uploaded_file, remote_path)
        st.success(f"File {uploaded_file.name} uploaded successfully!")

    def setup_fresh_retriever(_index, _embedding):
        logger.info("*" * 100)
        logger.info("Setting up a fresh retriever")

        # Clear the cache on the setup_retriever() function to let it run again
        setup_retriever.clear()
        setup_retriever(_index, _embedding)

        logger.info("*" * 100)
        logger.info("Retriever is refreshed")
        logger.info("*" * 100)

    # App layout
    st.title("Upload Documents")

    # Get the Pinecone index and the embedding model
    index = setup_pinecone_index()
    embedding = setup_embedding()

    uploaded_file = st.file_uploader("Upload File", type="pdf")

    # Upload and save file
    if uploaded_file:
        # Upload file to Firebase Storage
        upload_file(uploaded_file)

        # Restart the retriever to include the new file
        try:
            setup_fresh_retriever(index, embedding)
        except Exception as e:
            logger.info("*" * 100)
            logger.error(f"Error setting up retriever while uploading file: {e}")
            logger.info("*" * 100)

            remote_path = os.path.join(settings.DOCUMENTS_DIR, uploaded_file.name)
            delete_file_from_storage(remote_path)

    # List all files in storage
    st.write("###")
    st.subheader("Uploaded Files")

    files = get_files_in_folder_from_storage()
    if files:
        for file in files:

            st.write(f"📄 **{file.name}**")
            st.write(
                f"""Size: {file.size} bytes,
                Type: {file.content_type},
                Uploaded Time: {file.time_created.ctime()}
            """
            )

            # Download button
            st.download_button(
                label="Download",
                data=file.download_as_bytes(),
                file_name=file.name.split("/")[-1],
                mime="application/octet-stream",
            )

            # Delete button
            if st.button(f"Delete {file.name}", key=file.name):
                # Delete the file from the storage
                delete_file_from_storage(file.name)
                st.warning(f"{file.name} deleted.")

                # Restart the retriever to exclude the deleted file
                try:
                    setup_fresh_retriever(index, embedding)
                except Exception as e:
                    logger.info("*" * 100)
                    logger.error(f"Error setting up retriever after deleting file: {e}")
                    logger.info("*" * 100)

                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Create a temporary directory to download the file
                        file_path = os.path.abspath(f"{temp_dir}/{file.name}")
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        # Download the file to the temporary directory
                        file.download_to_filename(file_path)

                        # Upload the file back to the storage if error
                        upload_file_to_storage(file_path)

                st.rerun()

            st.write("####")

    else:
        st.write("No files uploaded yet.")


if __name__ == "__main__":
    main()
