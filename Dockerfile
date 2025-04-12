# Базовый образ Python
FROM python:3.10-slim  

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Сначала копируем только requirements.txt для кэширования слоев
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Команда для запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]