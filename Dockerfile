# Python + Debian slim
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
COPY . /app

# Instala dependencias y soporte para zona horaria
RUN apt-get update && \
    apt-get install -y tzdata && \
    pip install --no-cache-dir -r requirements.txt

# Zona horaria
ENV TZ=America/Argentina/Buenos_Aires
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Vars de entorno (igual que las tuyas)
ENV APP_NAME=ariadna \
    AUTH_HOST=icia-monitoreo \
    AUTH_PORT=8004 \
    AUTH_KEY=clave \
    DEVELOPMENT=False \
    LOGGER=True \
    LOGGER_LEVEL=None \
    DB_HOST=172.17.0.1 \
    DB_PORT=3306 \
    DB_USER=simon \
    DB_PASS=monitoreo \
    DATABASE=ariadna \
    AUTH_HOST=172.17.0.1 \
    AUTH_PORT=8004 \
    HELIOS_HOST=172.17.0.1 \
    HELIOS_PORT=8005 \
    REDIS_HOST=172.17.0.1 \
    REDIS_PORT=6379 \
    SESSION_EXPIRE=360

EXPOSE 8008

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8008", "--workers", "1"]
