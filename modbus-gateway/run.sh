#!/usr/bin/with-contenv bashio
set -euo pipefail

# Read configuration from add-on options
MODBUS_TCP_HOST=$(bashio::config 'modbus_tcp_host')
MODBUS_TCP_PORT=$(bashio::config 'modbus_tcp_port')
MODBUS_UNIT_ID=$(bashio::config 'modbus_unit_id')
REGISTER_COUNT=$(bashio::config 'register_count')
SERIAL_ENABLED=$(bashio::config 'serial_enabled')
SERIAL_PORT=$(bashio::config 'serial_port')
SERIAL_BAUDRATE=$(bashio::config 'serial_baudrate')
SERIAL_PARITY=$(bashio::config 'serial_parity')
SERIAL_STOPBITS=$(bashio::config 'serial_stopbits')
SERIAL_BYTESIZE=$(bashio::config 'serial_bytesize')
SERIAL_TIMEOUT=$(bashio::config 'serial_timeout')

bashio::log.info "Starting Modbus Gateway with TCP: $MODBUS_TCP_HOST:$MODBUS_TCP_PORT"

SERIAL_FLAG=""
if bashio::config.true 'serial_enabled'; then
  bashio::log.info "Serial enabled on $SERIAL_PORT (baud: $SERIAL_BAUDRATE)"
  if [[ ! -e "$SERIAL_PORT" ]]; then
    bashio::log.error "Serial port does not exist: $SERIAL_PORT"
    exit 1
  fi
  SERIAL_FLAG="--serial-enabled"
else
  bashio::log.info "Serial disabled"
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
