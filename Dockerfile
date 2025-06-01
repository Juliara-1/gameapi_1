# Используем официальный образ Python
FROM python:3.10

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED 1
WORKDIR /game_service

# Копируем файлы проекта
COPY requirements.txt requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код проекта
COPY . .

# Открываем порт Django (если используется runserver)
EXPOSE 8000

# Запуск приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
