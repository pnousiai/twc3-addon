import argparse
import logging
import threading
from pathlib import Path

from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server.sync import StartSerialServer, StartTcpServer
from pymodbus.transaction import ModbusAsciiFramer, ModbusRtuFramer


def build_context(register_count: int, unit_id: int) -> ModbusServerContext:
    holding = ModbusSequentialDataBlock(0, [0] * register_count)
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * register_count),
        co=ModbusSequentialDataBlock(0, [0] * register_count),
        hr=holding,
        ir=ModbusSequentialDataBlock(0, [0] * register_count),
        zero_mode=True,
    )
    return ModbusServerContext(slaves={unit_id: store}, single=False)


def build_identity() -> ModbusDeviceIdentification:
    identity = ModbusDeviceIdentification()
    identity.VendorName = "Home Assistant Modbus Gateway"
    identity.ProductCode = "HAGW"
    identity.VendorUrl = "https://www.home-assistant.io/"
    identity.ProductName = "Modbus TCP/RTU Gateway"
    identity.ModelName = "ModbusGateway"
    identity.MajorMinorRevision = "1.0"
    return identity


def start_tcp_server(context: ModbusServerContext, host: str, port: int, identity: ModbusDeviceIdentification) -> None:
    logging.info("Starting Modbus TCP server on %s:%s", host, port)
    StartTcpServer(
        context,
        identity=identity,
        address=(host, port),
        allow_reuse_address=True,
        allow_reuse_port=True,
    )


def start_serial_server(
    context: ModbusServerContext,
    port: str,
    baudrate: int,
    parity: str,
    stopbits: int,
    bytesize: int,
    timeout: int,
    identity: ModbusDeviceIdentification,
) -> None:
    if not Path(port).exists():
        raise SystemExit(f"Serial port does not exist: {port}")

    logging.info(
        "Starting Modbus RTU serial slave on %s baud=%s parity=%s stopbits=%s bytesize=%s timeout=%s",
        port,
        baudrate,
        parity,
        stopbits,
        bytesize,
        timeout,
    )

    StartSerialServer(
        context,
        identity=identity,
        port=port,
        framer=ModbusRtuFramer,
        timeout=timeout,
        baudrate=baudrate,
        parity=parity,
        stopbits=stopbits,
        bytesize=bytesize,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Home Assistant Modbus TCP/RTU gateway")
    parser.add_argument("--tcp-host", default="0.0.0.0", help="TCP bind host")
    parser.add_argument("--tcp-port", type=int, default=502, help="Modbus TCP port")
    parser.add_argument("--unit-id", type=int, default=1, help="Modbus unit identifier")
    parser.add_argument("--register-count", type=int, default=100, help="Number of registers in the Modbus datastore")
    parser.add_argument("--serial-enabled", action="store_true", help="Run the serial RTU slave server")
    parser.add_argument("--serial-port", default="/dev/ttyUSB0", help="Serial device path")
    parser.add_argument("--serial-baudrate", type=int, default=9600, help="Serial baud rate")
    parser.add_argument("--serial-parity", default="N", choices=["N", "E", "O"], help="Serial parity")
    parser.add_argument("--serial-stopbits", type=int, default=1, choices=[1, 2], help="Serial stop bits")
    parser.add_argument("--serial-bytesize", type=int, default=8, choices=[5, 6, 7, 8], help="Serial byte size")
    parser.add_argument("--serial-timeout", type=int, default=1, help="Serial timeout seconds")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

    context = build_context(args.register_count, args.unit_id)
    identity = build_identity()

    if args.serial_enabled:
        serial_thread = threading.Thread(
            target=start_serial_server,
            args=(
                context,
                args.serial_port,
                args.serial_baudrate,
                args.serial_parity,
                args.serial_stopbits,
                args.serial_bytesize,
                args.serial_timeout,
                identity,
            ),
            daemon=True,
        )
        serial_thread.start()
    else:
        logging.info("Serial RTU slave disabled; only TCP server will run.")

    start_tcp_server(context, args.tcp_host, args.tcp_port, identity)


if __name__ == "__main__":
    main()
