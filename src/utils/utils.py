import time
from enum import Enum

import streamlit as st

from utils.firebase import delete_blob_from_storage, delete_user_by_uid
from utils.rag import delete_namespace_in_vector_database


class MessageType(Enum):
    """
    Enum class to define the type of message to display.
    """

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


def display_message(type: MessageType, message: str = ""):
    """
    Function to display a success or error message banner that disappears after
    a few seconds.

    Args:
        type (MessageType): The type of message to display.
    """
    if type == "success":
        banner = st.success(message)
    elif type == "error":
        banner = st.error(message)
    else:
        banner = st.warning(message)

    time.sleep(4)
    banner.empty()


@st.dialog("⚠ DELETE ACCOUNT ⚠")
def delete_account(uid: str):
    """
    Popup dialog to confirm if the user wants to delete their account and delete
    the account if the user confirms.

    Args:
        uid (str): The user's Firebase UID
    """

    st.write("Are you sure you want to DELETE this account?")
    _, no, yes = st.columns([5, 1, 1])
    no_clicked = no.button("No", key="no", use_container_width=True)
    yes_clicked = yes.button("Yes", key="yes", use_container_width=True)

    if no_clicked:
        st.rerun()
    elif yes_clicked:
        # Delete user's namespace in Pinecone (and the record manager cache)
        delete_namespace_in_vector_database(uid)
        # Delete user's folder in Firebase Storage
        delete_blob_from_storage(uid)
        # Delete user in Firebase Authentication
        delete_user_by_uid(uid)
        # Remove the session state since the user has deleted the account
        for key in st.session_state.keys():
            st.session_state.pop(key, None)
        st.rerun()
