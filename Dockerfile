FROM python:3.11-slim

COPY . /app

WORKDIR /app

RUN pip install --no-cache-dir uv

RUN uv sync

CMD ["uv", "run", "main.py"]