FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

# for cache
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . /app

RUN mkdir -p /data/chromadb /data/sqlite3

CMD [ "python3", "main.py" ]