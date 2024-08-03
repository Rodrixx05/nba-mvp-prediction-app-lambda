FROM python:3.8.6-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT sleep 10 && mlflow server --workers 1 --static-prefix /mlflow

