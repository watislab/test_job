FROM python:3.9-slim-buster

WORKDIR /app

COPY . /app  # Копируем все из контекста сборки в /app

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "/app/main.py"]