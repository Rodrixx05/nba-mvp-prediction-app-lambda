FROM python:3.8.6-slim-buster

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT sleep 10 && mlflow server --app-name basic-auth --workers 1 --static-prefix /mlflow

