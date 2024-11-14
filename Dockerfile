# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с ботом и зависимости в контейнер
COPY telegram_bot.py /app/telegram_bot.py
COPY requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Указываем команду запуска бота
CMD ["python3", "telegram_bot.py"]
