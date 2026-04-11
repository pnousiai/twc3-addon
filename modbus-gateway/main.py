import argparse
import asyncio
import logging
from pathlib import Path

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusDeviceContext,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartAsyncTcpServer, StartAsyncSerialServer


def build_context(register_count: int, unit_id: int) -> ModbusServerContext:
    store = ModbusDeviceContext(
        di=ModbusSequentialDataBlock(0, [0] * register_count),
        co=ModbusSequentialDataBlock(0, [0] * register_count),
        hr=ModbusSequentialDataBlock(0, [0] * register_count),
        ir=ModbusSequentialDataBlock(0, [0] * register_count),
    )
    return ModbusServerContext(devices={unit_id: store}, single=False)


def build_identity() -> ModbusDeviceIdentification:
    identity = ModbusDeviceIdentification()
    identity.VendorName = "Home Assistant Modbus Gateway"
    identity.ProductCode = "HAGW"
    identity.VendorUrl = "https://www.home-assistant.io/"
    identity.ProductName = "Modbus TCP/RTU Gateway"
    identity.ModelName = "ModbusGateway"
    identity.MajorMinorRevision = "1.0"
    return identity


async def start_tcp_server(context, host, port, identity):
    logging.info("Starting Modbus TCP server on %s:%s", host, port)
    await StartAsyncTcpServer(
        context=context,
        identity=identity,
        address=(host, port),
    )


async def start_serial_server(
    context,
    port,
    baudrate,
    parity,
    stopbits,
    bytesize,
    timeout,
    identity,
):
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

    await StartAsyncSerialServer(
        context=context,
        identity=identity,
        port=port,
        baudrate=baudrate,
        parity=parity,
        stopbits=stopbits,
        bytesize=bytesize,
        timeout=timeout,
    )


async def main():
    parser = argparse.ArgumentParser(description="Home Assistant Modbus TCP/RTU gateway")
    parser.add_argument("--tcp-host", default="0.0.0.0")
    parser.add_argument("--tcp-port", type=int, default=502)
    parser.add_argument("--unit-id", type=int, default=1)
    parser.add_argument("--register-count", type=int, default=100)

    parser.add_argument("--serial-enabled", action="store_true")
    parser.add_argument("--serial-port", default="/dev/ttyUSB0")
    parser.add_argument("--serial-baudrate", type=int, default=9600)
    parser.add_argument("--serial-parity", default="N", choices=["N", "E", "O"])
    parser.add_argument("--serial-stopbits", type=int, default=1, choices=[1, 2])
    parser.add_argument("--serial-bytesize", type=int, default=8, choices=[5, 6, 7, 8])
    parser.add_argument("--serial-timeout", type=int, default=1)

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

    context = build_context(args.register_count, args.unit_id)
    identity = build_identity()

    tasks = []

    if args.serial_enabled:
        tasks.append(
            start_serial_server(
                context,
                args.serial_port,
                args.serial_baudrate,
                args.serial_parity,
                args.serial_stopbits,
                args.serial_bytesize,
                args.serial_timeout,
                identity,
            )
        )
    else:
        logging.info("Serial RTU slave disabled; only TCP server will run.")

    tasks.append(start_tcp_server(context, args.tcp_host, args.tcp_port, identity))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())