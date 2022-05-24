FROM python:3.10-slim-buster
WORKDIR /flask
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
EXPOSE 5000