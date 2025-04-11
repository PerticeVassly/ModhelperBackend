FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

RUN mkdir -p /data/chromadb /data/sqlite3

CMD [ "python3", "main.py" ]