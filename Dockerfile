FROM python:3.12.7-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt -U

COPY src /app/src

CMD ["streamlit", "run", "src/Home.py", "--server.port", "8080"]
