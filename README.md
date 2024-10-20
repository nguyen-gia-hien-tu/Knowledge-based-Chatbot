# Knowlege-based Chatbot

Welcome to the knowledge-based chatbot application using the RAG pipeline

## End-to-End Steps to Create the Chatbot


### Copy .env.example to .env

- Copy and Paste the file `.env.example` to create a new file called `.env`

- We will modify the file `.env` to store API keys and configurations


### Create a Firebase Project

- Go to the [Firebase console](https://console.firebase.google.com/u/0/)

- Click on **"Create a project"** button to create a new Firebase project

- Enter the project name and click the **"Continue"** button

- After the project is created and you are in the project, click on the
  **"Settings"** icon (the ⚙️ icon)

- Then, navigate to the **"Service accounts"** tab and click **"Generate new
  private key"** button to create a new service account

- Then name the file `firebase-service-account.json` and put it in the root of
  the repository (where you see the `src/` folder)

- Ensure that the values for both `GOOGLE_APPLICATION_CREDENTIALS` and
  `FIREBASE_SERVICE_ACCOUNT_FILE` are `firebase-service-account.json`


### Create Storage in the Firebase project

- Inside the created Firebase project, choose the **"Storage"** service

- Click on **"Get started"** button to create a bucket

- Copy the bucket name, including the `gs://` part and put it as the value of
  the `FIREBASE_STORAGE_REMOTE_PATH` in the `.env` file


### Create a Gemini AI API Key to call the Gemini Model

- Go to the [Google AI Studio](https://aistudio.google.com/) website

- Click on the **"Get API key"** button

- Then, click on the **"Create API key"** button

- Select the Firebase project created in the earlier step

- Click the **"Create API key in existing project"** button

- Copy the API key and put it as the value for `GEMINI_API_KEY` in the `.env`
  file


### Create a Pinecone account to store vectors

- Go to [Pinecone](https://www.pinecone.io/) website

- Sign up or sign in to Pinecone

- Click on the **"API keys"** tab on the left-hand panel

- Click the **"Create API key"** button to generate a new API key

- Give this API key a name and copy the token

- Paste the API key content to the `PINECONE_API_KEY` entry in the `.env` file


### Create LangSmith project for tracing

- Go to [LangSmith](https://smith.langchain.com/) website

- Sign up or sign in to LangSmith

- Click on the **"+ New Project"** button to create a new LangSmith project

- Select the **"With LangChain"** option and follow the provided steps

- Copy the key-value entries and put them in the `.env` file


### Install the requirements packages

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

### Run the application

- Make sure you are at the root of the repository

- Then run the application with

  ```bash
  streamlit run src/chatbot.py
  ```
