FROM python:3.8.6-slim-buster

LABEL maintainer "Marc Rodriguez, marc.rodri5@gmail.com.com"

# set working directory in container
WORKDIR /usr/src/app

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# Copy and install packages
COPY requirements.txt /
RUN pip install --upgrade pip && pip install -r /requirements.txt

# Copy app folder to app folder in container
COPY /app /usr/src/app/

# Changing to non-root user
RUN useradd -m appUser
USER appUser