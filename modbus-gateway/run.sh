#!/usr/bin/env bashio
set -euo pipefail

MODBUS_TCP_HOST="${MODBUS_TCP_HOST:-0.0.0.0}"
MODBUS_TCP_PORT="${MODBUS_TCP_PORT:-503}"
MODBUS_UNIT_ID="${MODBUS_UNIT_ID:-1}"
REGISTER_COUNT="${REGISTER_COUNT:-40010}"
SERIAL_ENABLED="${SERIAL_ENABLED:-true}"
SERIAL_PORT="${SERIAL_PORT:-/dev/ttyUSB0}"
SERIAL_BAUDRATE="${SERIAL_BAUDRATE:-115200}"
SERIAL_PARITY="${SERIAL_PARITY:-N}"
SERIAL_STOPBITS="${SERIAL_STOPBITS:-1}"
SERIAL_BYTESIZE="${SERIAL_BYTESIZE:-8}"
SERIAL_TIMEOUT="${SERIAL_TIMEOUT:-1}"

SERIAL_FLAG=""
if [[ "${SERIAL_ENABLED,,}" == "true" || "${SERIAL_ENABLED}" == "1" ]]; then
  SERIAL_FLAG="--serial-enabled"
fi

exec /opt/venv/bin/python /app/main.py \
  --tcp-host "$MODBUS_TCP_HOST" \
  --tcp-port "$MODBUS_TCP_PORT" \
  --unit-id "$MODBUS_UNIT_ID" \
  --register-count "$REGISTER_COUNT" \
  $SERIAL_FLAG \
  --serial-port "$SERIAL_PORT" \
  --serial-baudrate "$SERIAL_BAUDRATE" \
  --serial-parity "$SERIAL_PARITY" \
  --serial-stopbits "$SERIAL_STOPBITS" \
  --serial-bytesize "$SERIAL_BYTESIZE" \
  --serial-timeout "$SERIAL_TIMEOUT"
