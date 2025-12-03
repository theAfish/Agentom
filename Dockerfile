FROM python:3.9-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The workspace will be mounted at runtime