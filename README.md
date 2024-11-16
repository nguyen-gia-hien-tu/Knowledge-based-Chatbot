# Knowlege-based Chatbot

Welcome to the knowledge-based chatbot application using the RAG pipeline 🤖

## Application Link

To access the application, go to
[https://knowledge-based-chatbot-app.streamlit.app/](https://knowledge-based-chatbot-app.streamlit.app/)


## End-to-End Steps to Setup the Chatbot


### Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and `record_manager_cache.db.example` to `record_manager_cache.db`

- Copy and Paste the file `.secrets.toml.example` in the `.streamlit/` folder
  and rename the new file to `.secrets.toml`

  - This file is used to store the secrets that will be used in the application

- Copy and Paste the file `record_manager_cache.db.example` and rename the new
  file to `record_manager_cache.db`

  - This file is a cache file for LangChain Indexing API to load data into the
    vector database

- We will modify the file `.streamlit/secrets.toml` to store API keys and
  configuration later on


### Create a Firebase Project

- Go to the [Firebase console](https://console.firebase.google.com)

- Click on **"Create a project"** button to create a new Firebase project

- Enter the project name and click the **"Continue"** button

- After the project is created and you are in the project, click on the
  **"Settings"** icon (the ⚙️ icon) and click on **"Project settings"**

- Then, navigate to the **"Service accounts"** tab and click **"Generate new
  private key"** button to create a new service account

- Download the file to a location of your choice (since we only need the content
  of the file, not the file location). Now, copy the value of each key to the
  corresponding key in the `secrets.toml` file, under the
  `[FIREBASE_SERVICE_ACCOUNT]` section

  - This `FIREBASE_SERVICE_ACCOUNT` section is used to initialize the Firebase
    Admin SDK

  - It is also used to programmatically create the
    `firebase-service-account.json` file

  - The `firebase-service-account.json` file is referred by the
    `GOOGLE_APPLICATION_CREDENTIALS` environment variable, which is used to
    instantiate the connection for Google Gemini API

- Now, on the same "Project settings" page, go to the **"General"** tab and
  locate the **"Web API Key"** entry

- Copy the value of this "Web API Key" and put it as the value for the
  **"FIREBASE_API_KEY"** in the `secrets.toml` file


### Create Storage in the Firebase project

- Inside the created Firebase project, choose the **"Storage"** service

- Click on **"Get started"** button to create a bucket

- Copy the bucket name, *excluding* the `gs://` part, while *including* the
  `.appspot.com` part and put it as the value of the
  `FIREBASE_STORAGE_BUCKET_NAME` in the `.secrets.toml` file


### Create an OAuth 2.0 Client ID for Google Single-Sign On

- To enable "Log In with Google" feature, we need to enable **"Google"** in the
  "Sign-in providers" section

- Go to the created Firebase project and click on the **"Authentication"**
  product

- Then click on the **"Sign-in method"** tab and then, the **"Add new
  provider"** button

- Click on the **"Enable"** toggle to enable the Google provider

  - A drop down will appear to update "Public-facing name for project" and
    "Support email for project"

  - Enter a preferred name for the "Public-facing name for project"

  - Select the email address used to create the Firebase project for "Support
    email for project"

  - Then, click **"Save"**

- After Firebase finishes creating the client ID for "Sign in with Google"
  feature, go to the [Google Cloud
  Credentials](https://console.cloud.google.com/apis/credentials) page to
  download the client secret file

- In the Google Cloud Credentials page, there is a section for **"OAuth 2.0
  Client IDs"** with 1 entry. This entry is the client ID that we created above

- Click on the entry for client ID

- On the **"Client secrets"** section, there is a client secret shown along with
  a "Download JSON" button

- Download the file to a location of your choice (since we only need the content
  of the file, not the file location) and copy the value of each key to the
  corresponding key in the `secrets.toml` file, under the
  `[GOOGLE_OIDC_CLIENT_SECRET]` section


  - This `GOOGLE_OIDC_CLIENT_SECRET` is used for the "Sign-in with Google"
    feature using streamlit-oauth library

- Continue on this credentials page, locate the **"Authorized redirect URIs"**
  section

- Click on the **"Add URI"** button and enter **"http://localhost:8080"**, then
  press Enter

  - This is the URL with the port number where our Streamlit knowledge-based
    chatbot application locally runs on

  - **_NOTE_:** When deploying to an actual hosting site, we will also need to
    add that URL to the "Authorized redirect URIs" section

- Make sure the `GOOGLE_OIDC_REDIRECT_URI` in the `.secrets.tml` file has the
  value of `http://localhost:8080` for local development


### Create a Gemini AI API Key to Call the Gemini Model

- Go to the [Google AI Studio](https://aistudio.google.com) website

- Click on the **"Get API key"** button

- Then, click on the **"Create API key"** button

- Select the Firebase project created in the earlier step

- Click the **"Create API key in existing project"** button

- Copy the API key and put it as the value for `GEMINI_API_KEY` in the
  `.secrets.toml` file


### Create a Pinecone Account to Store Vectors

- Go to [Pinecone](https://www.pinecone.io) website

- Sign up or sign in to Pinecone

- Click on the **"API keys"** tab on the left-hand panel

- Click the **"Create API key"** button to generate a new API key

- Give this API key a name and copy the token

- Paste the API key content to the `PINECONE_API_KEY` entry in the `.env` file


### Create LangSmith Project for Tracing

- Go to [LangSmith](https://smith.langchain.com) website

- Sign up or sign in to LangSmith

- Click on the **"+ New Project"** button to create a new LangSmith project

- Select the **"With LangChain"** option and follow the provided steps

- Copy the key-value entries and put them in the `.secrets.toml` file (i.e.,
  replace the 4 keys that start with `LANGCHAIN_` in the `.secrets.toml` file)


### Run the Application

There are 2 ways to run the application. with or without Docker

- To run the application without Docker, expand the below step

  <details>
    <summary>Without Docker</summary>

    To run the application without Docker, you need to install Python 3.12,
    create a Python virtual environment and run the application with `streamlit`

    #### Install Python 3.12

    For the best consistency, please go to the
    [Python](https://www.python.org/downloads/) download page and download
    Python version 3.12.

    #### Install the requirements packages

    - At the root of the repository, create a Python virtual environment with

      ```bash
      python -m venv .venv
      ```

    - Then activate the environment with

      - For MacOS or Linux

        ```bash
        source .venv/bin/activate
        ```

      - For Windows

        ```powershell
        .\.venv\Script\activate
        ```

    #### Run the application

    - Make sure you are at the root of the repository

    - Then run the application with

      ```bash
      streamlit run src/home.py --server.port 8080
      ```
  </details>

- To run the application with Docker, expand the below step

  <details>
    <summary>With Docker</summary>

    #### Install Docker Desktop

    To install Docker, the easiest way is to install Docker Desktop. Please go
    to the [Docker download](https://docs.docker.com/get-started/get-docker/)
    page to install Docker Desktop on your machine.

    #### Install Docker Compose

    Docker Compose should come pre-installed with Docker Desktop. For further
    information, please refer to the [Docker Compose
    Installation](https://docs.docker.com/compose/install/) guide.

    #### Run the application with Docker

    - To run the application with Docker, run the following command at the root
      of the respository (where you see the `src/` folder)

      ```bash
      docker compose up -d --build
      ```

    - Now, you can view the log of the container with

      ```bash
      docker compose logs -f chatbot
      ```

  </details>

### View the Application

To view the application after starting it up, simply go to
[http://localhost:8080](http://localhost:8080)
