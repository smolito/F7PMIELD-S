FROM python:3.10-slim

# fancy performance optimizations
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Výchozí příkaz, který se spustí při startu kontejneru
CMD ["python", "manage.py", "runserver", "127.0.0.1:8000"]
