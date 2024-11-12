import json
import logging

import streamlit as st

from configuration import settings
from utils.firebase import (
    authenticate_user_with_google_oidc,
    authenticate_user_with_password,
    get_user_by_token,
)
from utils.utils import display_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def login_form():
    """
    Display the login form where users can log in with their email and password
    and use the Google Sign-in feature.
    """

    #################################################################
    # Email and Password Login
    #################################################################
    with st.form(key="login_form"):
        st.write("Enter your email and password to log in:")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Log In")

    if submit_button:
        if email == "" or password == "":
            display_message(
                type="warning", message="Please enter your email and password."
            )
        elif user_obj := authenticate_user_with_password(email, password):
            logger.info("*" * 100)
            logger.info("Successfully logged in with email and password!")
            logger.info("*" * 100)

            if user_info := get_user_by_token(user_obj["idToken"]):
                st.session_state["logged_in"] = True
                st.session_state["sso"] = False
                st.session_state["uid"] = user_info.uid
                st.session_state["name"] = user_info.display_name
                st.session_state["email"] = user_info.email
                st.rerun()
        else:
            display_message(
                type="error",
                message="Invalid email or password. Please try again.",
            )

    st.divider()

    #################################################################
    # Google Sign-in Login
    #################################################################
    st.markdown(
        f"<h4 style='text-align: center'>Or log in with service provider</h4>",
        unsafe_allow_html=True,
    )

    client_secret = st.secrets["GOOGLE_OIDC_CLIENT_SECRET"]
    redirect_uri = settings.GOOGLE_OIDC_REDIRECT_URI

    client_id = client_secret["web"]["client_id"]
    google_oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=openid%20email%20profile&output=embed"

    google_button_css = """
        <style>
            /* Container for the button */
            .google-btn {
                display: inline-block;
                align-items: center;
                padding: 10px 15px;
                border: 1px solid #4285f4;
                border-radius: 5px;
                background-color: #cacfd2;
                cursor: pointer;
                text-decoration: none;
                color: #00ffff;
                font-family: Arial, sans-serif;
                font-weight: 500;
                font-size: 16px;
                transition: background-color 0.3s ease;
            }

            /* Google logo */
            .google-btn img {
                width: 20px;
                height: 20px;
                margin-right: 10px;
            }

            /* Hover effect */
            .google-btn:hover {
                background-color: #f0f0f0;
            }
        </style>
        """

    st.markdown(google_button_css, unsafe_allow_html=True)

    google_button_html = f"""
        <!-- Google Button -->
        <div style="text-align: center">
        <a style="color: black; font-weight: bold" href="{google_oauth_url}" target="_top" class="google-btn">
            <img src="https://www.gstatic.com/images/branding/product/1x/gsa_48dp.png" alt="Google logo">
            Sign in with Google
        </a>
        </div>
    """

    st.markdown(google_button_html, unsafe_allow_html=True)

    auth_code = st.query_params.get("code")

    if auth_code:
        firebase_user = authenticate_user_with_google_oidc(
            auth_code, st.secrets["GOOGLE_OIDC_CLIENT_SECRET"]
        )

        logger.info("*" * 100)
        logger.info("Succesfully logged in with Google!")
        logger.info("*" * 100)

        st.session_state["logged_in"] = True
        st.session_state["sso"] = True
        st.session_state["uid"] = firebase_user.uid
        st.session_state["name"] = firebase_user.display_name
        st.session_state["email"] = firebase_user.email

        st.rerun()
