import streamlit as st

from utils.firebase import reset_password
from utils.utils import display_message


def reset_password_form():
    """
    Display the reset password form where users can reset their password by
    email
    """
    form = st.form("Reset Password")
    form.write("Enter your email to reset your password:")
    email = form.text_input("Email")
    reset_password_button = form.form_submit_button("Reset Password")

    if reset_password_button:
        reset_password(email)

        display_message(
            type="success",
            message=f"If you have an account with email: {email}, "
            "please check your email to reset password.",
        )
