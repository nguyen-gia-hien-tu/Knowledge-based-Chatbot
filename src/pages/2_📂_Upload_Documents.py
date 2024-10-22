import mimetypes
import os
import time

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from configuration import settings
from utils.utils import setup_embedding, setup_pinecone_index, setup_retriever


def main():

    # Create directory if it doesn't exist
    os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)

    # File upload function
    def upload_file(uploaded_file: UploadedFile):
        with open(os.path.join(settings.DOCUMENTS_DIR, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getvalue())
        st.success(f"File {uploaded_file.name} uploaded successfully!")

    # List files in storage
    def list_files_in_storage():
        file_list = []
        for path, _, files in os.walk(settings.DOCUMENTS_DIR):
            for file in files:
                relative_path = os.path.relpath(path, settings.DOCUMENTS_DIR)
                file_list.append(os.path.join(relative_path, file))
        return file_list

    # Display file metadata (size and upload time)
    def get_file_metadata(file_path):
        file_size = os.path.getsize(file_path)
        file_type, encoding = mimetypes.guess_type(file_path)
        upload_time = time.ctime(os.path.getctime(file_path))
        return file_size, file_type, upload_time

    def setup_fresh_retriever(_index, _embedding):
        print("*" * 100)
        print("Setting up a fresh retriever")
        setup_retriever.clear()
        setup_retriever(_index, _embedding)
        print("*" * 100)
        print("Retriever is refreshed")
        print("*" * 100)

    # App layout
    st.title("Upload Documents")

    # File upload
    index = setup_pinecone_index()
    embedding = setup_embedding()

    uploaded_file = st.file_uploader(
        "Upload File",
        type="pdf",
    )

    # Upload and save file
    if uploaded_file:
        upload_file(uploaded_file)
        try:
            setup_fresh_retriever(index, embedding)
        except Exception as e:
            st.error(f"Error: {e}")
            os.remove(os.path.join(settings.DOCUMENTS_DIR, uploaded_file.name))

    # List all files in storage
    st.write("###")
    st.subheader("Uploaded Files")
    files = list_files_in_storage()
    if files:
        for file in files:
            file_path = os.path.join(settings.DOCUMENTS_DIR, file)
            file_size, file_type, upload_time = get_file_metadata(file_path)

            st.write(f"📄 **{file}**")
            st.write(
                f"Size: {file_size} bytes, Type: {file_type}, Uploaded on: {upload_time}"
            )

            # Download button
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download",
                    data=f,
                    file_name=file,
                    mime="application/octet-stream",
                )

            # Delete button
            if st.button(
                f"Delete {file}",
                key=file,
            ):
                os.remove(file_path)
                st.warning(f"{file} deleted.")
                try:
                    setup_fresh_retriever(index, embedding)
                except Exception as e:
                    st.error(f"Error: {e}")
                    with st.spinner("Error while deleting!!! Reverting changes..."):
                        upload_file(file)
                st.rerun()

    else:
        st.write("No files uploaded yet.")


if __name__ == "__main__":
    main()
