import streamlit as st

from utils.firebase import create_new_user
from utils.utils import display_message


def register_form():
    """
    Display the registration form where users can register with their email and
    password.
    """
    with st.form(key="register_form"):
        st.write("Enter your email and password to register:")
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        register_button = st.form_submit_button("Register")

    if register_button:
        if password == confirm_password:
            try:
                user_info = create_new_user(email, password, name)
                display_message(
                    type="success",
                    message=f"Successfully registered user with email: {email}",
                )
                st.session_state["logged_in"] = True
                st.session_state["name"] = user_info.display_name
                st.session_state["email"] = user_info.email
                st.rerun()
            except Exception as e:
                display_message(type="error", message=str(e))
        else:
            display_message(
                type="error", message="Passwords do not match. Please try again."
            )
