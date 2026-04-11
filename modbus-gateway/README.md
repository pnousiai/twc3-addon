# Modbus Gateway Home Assistant Add-on

This repository contains a Home Assistant add-on scaffold that provides a `pymodbus` 3.x Modbus TCP server with optional serial RTU slave support.

## What is included

- `config.yaml` - Home Assistant add-on manifest compatible with `2026.x`
- `Dockerfile` - Builds a lightweight Python runtime on the Home Assistant base image
- `requirements.txt` - Installs `pymodbus>=3.0,<4.0` and `pyserial`
- `run.sh` - Entrypoint for the add-on container
- `main.py` - Modbus gateway that bridges TCP writes to serial RTU registers

## Purpose

This add-on listens as a Modbus TCP server for writes from Home Assistant. It can also expose the same holding register datastore over a serial RTU slave port, enabling a PLC to read register values via RS485.

## Configuration options

- `modbus_tcp_host`: TCP bind address for the Modbus server
- `modbus_tcp_port`: TCP port for Modbus requests
- `modbus_unit_id`: Modbus unit ID for the server context
- `register_count`: Number of registers in the shared datastore
- `serial_enabled`: Enable serial RTU slave mode
- `serial_port`: Serial device path, e.g. `/dev/ttyUSB0`
- `serial_baudrate`: Serial baud rate
- `serial_parity`: Serial parity (`N`, `E`, `O`)
- `serial_stopbits`: Serial stop bits (`1` or `2`)
- `serial_bytesize`: Serial byte size (`5`, `6`, `7`, or `8`)
- `serial_timeout`: Serial timeout in seconds

## Notes

- The add-on runs as a Modbus TCP server on the configured TCP port.
- When `serial_enabled` is true, the same register data is exposed over RTU serial.
- Register writes from TCP clients are available for PLCs reading from the RS485 serial slave.
- Make sure the add-on has access to the configured serial device from Home Assistant.
