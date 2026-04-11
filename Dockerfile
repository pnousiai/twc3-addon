ARG BUILD_FROM=ghcr.io/home-assistant/base:latest
FROM $BUILD_FROM

LABEL io.hass.type="app"
LABEL io.hass.version="2026.1.0"
LABEL io.hass.arch="amd64 aarch64 armv7 i386"

RUN apk add --no-cache python3 py3-pip
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py /app/
COPY run.sh /app/
RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
