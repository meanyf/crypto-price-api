# Используем официальный образ Python в качестве базового
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Скачиваем dockerize (версия можно поменять)
ENV DOCKERIZE_VERSION=v0.9.9
RUN wget -O /tmp/dockerize.tar.gz "https://github.com/jwilder/dockerize/releases/download/${DOCKERIZE_VERSION}/dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" && \
    tar -C /usr/local/bin -xzvf /tmp/dockerize.tar.gz && \
    rm /tmp/dockerize.tar.gz && \
    chmod +x /usr/local/bin/dockerize

# Копируем только requirements.txt, чтобы установить зависимости
COPY requirements.txt .

# Устанавливаем зависимости приложения
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 8000 для приложения
EXPOSE 8000

# Запускаем приложение с использованием uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
