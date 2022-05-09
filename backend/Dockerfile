FROM python:3.9-slim-buster
WORKDIR /fastapi
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]