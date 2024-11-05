import streamlit as st

from account import login_form, register_form, reset_password_form
from utils.firebase import update_user_info_by_email
from utils.rag import setup_tools
from utils.utils import display_message


def initialize_session_state():
    """
    Initialize the session state to cache user information.
    """
    session_key_val = {
        "name": None,
        "email": None,
        "logged_in": False,
        "sso": False,
    }

    for key, val in session_key_val.items():
        if key not in st.session_state:
            st.session_state[key] = val


def authentication():
    """
    Display the authentication page where users can log in, register, or reset
    their password.
    """

    st.title("Welcome to the Knowledge-based Chatbot! 🤖👋")

    st.markdown(
        """
        This is a knowledge-based chatbot where you can upload your own documents
        and chat with the AI assistant. The AI assistant will answer your questions
        based on the uploaded documents.

        Please log in or register to continue.
        """
    )

    login_tab, register_tab, reset_password_tab = st.tabs(
        ["Log In", "Register", "Reset Password"]
    )
    with login_tab:
        login_form()
    with register_tab:
        register_form()
    with reset_password_tab:
        reset_password_form()


def logout():
    """
    Display the logout form. This logs the user out and clears the cache.
    """
    with st.form("logout_form"):
        st.markdown(
            f"<h4 style='text-align: center'>Do you want to log out?</h4><br/>",
            unsafe_allow_html=True,
        )
        button = st.form_submit_button("Log Out", use_container_width=True)

    if button:
        st.session_state["logged_in"] = False
        # Remove the cache since the user has logged out
        for key in st.session_state.keys():
            st.session_state.pop(key, None)
        st.rerun()


def account_settings():
    """
    Display the account settings page where users can update their account
    information and password.
    """
    settings_tab, update_password_tab = st.tabs(["Settings", "Update Password"])

    ######################################################################
    # Settings tab
    ######################################################################
    with settings_tab.form("settings_form"):
        st.markdown("## Settings")
        st.text_input("Email", value=st.session_state["email"], disabled=True)
        name = st.text_input("Name", value=st.session_state["name"])
        save_button = st.form_submit_button("Save")

    if save_button:
        st.session_state["name"] = name
        update_user_info_by_email(st.session_state["email"], display_name=name)
        display_message(type="success", message="Settings saved successfully.")

    ######################################################################
    # Update Password tab
    ######################################################################
    with update_password_tab.form("update_password_form"):
        st.markdown("## Update Password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        update_password_button = st.form_submit_button("Update Password")

    if update_password_button:
        if new_password == confirm_new_password:
            # Update password
            update_user_info_by_email(st.session_state["email"], password=new_password)
            display_message(type="success", message="Password updated successfully.")
        else:
            display_message(
                type="error", message="Passwords do not match. Please try again."
            )


def main():
    """
    Main function to set logic and display the pages
    """

    st.set_page_config(
        page_title="Knowledge-based Chatbot",
        page_icon="🤖",
    )

    initialize_session_state()

    # Initialize Firebase app, setup LLM, vector database and retriever
    setup_tools()

    authentication_page = st.Page(page=authentication, title="Authentication")

    chatbot_page = st.Page(page="tools/chatbot.py", icon="🤖", title="Chatbot")
    upload_docs_page = st.Page(
        page="tools/upload_documents.py", icon="📁", title="Upload Documents"
    )

    settings_page = st.Page(page=account_settings, icon="⚙️", title="Settings")
    logout_page = st.Page(page=logout, icon=":material/logout:", title="Log Out")

    if st.session_state["logged_in"]:
        pg = st.navigation(
            {
                "Tools": [chatbot_page, upload_docs_page],
                "Account": [settings_page, logout_page],
            }
        )
    else:
        pg = st.navigation([authentication_page])

    pg.run()


if __name__ == "__main__":
    main()
