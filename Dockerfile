# Базовый образ Python
FROM python:3.9-slim

# Рабочая директория
WORKDIR /app

# Копируем requirements.txt в /app/requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]