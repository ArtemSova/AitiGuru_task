FROM python:3.13-slim


# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
libpq-dev gcc \
&& rm -rf /var/lib/apt/lists/*


# Создаем рабочую директорию
WORKDIR /app


# Устанавливаем Python зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


# Копируем проект
COPY . .


# Указываем порт
EXPOSE 8000


# Запуск через gunicorn
CMD ["gunicorn", "aitiguru.wsgi:application", "--bind", "0.0.0.0:8000"]