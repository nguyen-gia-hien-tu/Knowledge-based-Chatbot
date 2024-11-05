FROM python:3.12.7-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt -U

COPY src /app/src

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "src/home.py", "--server.port", "8080"]
