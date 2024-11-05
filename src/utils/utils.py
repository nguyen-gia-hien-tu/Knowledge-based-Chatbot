from enum import Enum
import time

import streamlit as st


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
