import json
import logging

import firebase_admin
import requests
import streamlit as st
from firebase_admin import auth, credentials
from google_auth_oauthlib import flow


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Firebase Admin setup
cred = credentials.Certificate("../firebase-service-account.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Google OAuth 2.0 Client setup
with open("../firebase-google-oidc-client-secret.json") as f:
    client_secret = json.load(f)
client_id = client_secret["web"]["client_id"]
client_secrets_file = "../firebase-google-oidc-client-secret.json"
redirect_uri = "http://localhost:8501"  # Your Streamlit app URL

# Streamlit app
st.title("Sign in with Google")

# Authentication workflow
if "google_user" not in st.session_state:
    # Step 1: Display the sign-in button
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=openid%20email%20profile"

    st.markdown(f"[Sign in with Google]({auth_url})")

    # Step 2: Capture the redirect from Google and exchange for token
    auth_code = st.query_params.get("code")

    if auth_code:
        # Use authorization code to fetch token from Google
        flow = flow.Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
            ],
        )
        flow.redirect_uri = redirect_uri
        flow.fetch_token(code=auth_code)

        # Obtain Google user info
        credentials = flow.credentials
        google_user = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"},
        ).json()

        # Firebase Authentication: Create a custom token
        firebase_token = auth.create_custom_token(google_user["sub"])

        # Store user info and token in session state
        st.session_state["google_user"] = google_user
        st.session_state["firebase_token"] = firebase_token

# Display user information if signed in
if "google_user" in st.session_state:
    st.write("Signed in as:", st.session_state["google_user"]["email"])
    st.write("Google user data:", st.session_state["google_user"])
    st.write("Firebase token:", st.session_state["firebase_token"])
