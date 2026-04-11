ARG BUILD_FROM=ghcr.io/home-assistant/base-python:3.12
FROM $BUILD_FROM

LABEL io.hass.type="app"
LABEL io.hass.version="2026.1.0"
LABEL io.hass.arch="amd64 aarch64"

ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app

RUN apk add --no-cache python3 py3-pip
COPY requirements.txt /app/
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY main.py /app/
COPY run.sh /app/
RUN chmod +x /app/run.sh
CMD ["/app/run.sh"]
