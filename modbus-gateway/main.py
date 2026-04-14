import argparse
import asyncio
import logging
from pathlib import Path

from pymodbus import ModbusDeviceIdentification
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusDeviceContext,
)
from pymodbus.server import StartAsyncTcpServer, StartAsyncSerialServer


# 🔍 Logging DataBlock
class LoggingDataBlock(ModbusSequentialDataBlock):
    def getValues(self, address, count=1):
        values = super().getValues(address, count)
        logging.info(
            "[READ] addr=%s count=%s -> %s",
            address,
            count,
            values,
        )
        return values

    def setValues(self, address, values):
        logging.info(
            "[WRITE] addr=%s values=%s",
            address,
            values,
        )
        super().setValues(address, values)


def build_context(register_count: int, unit_id: int) -> ModbusServerContext:
    if register_count > 65535:
        raise ValueError(
            f"register_count must be <= 65535 (Modbus address limit), got {register_count}"
        )
    
    device = ModbusDeviceContext(
        di=LoggingDataBlock(1, [0] * register_count),
        co=LoggingDataBlock(1, [0] * register_count),
        hr=LoggingDataBlock(1, [0] * register_count),
        ir=LoggingDataBlock(1, [0] * register_count),
    )

    return ModbusServerContext(devices={unit_id: device}, single=False)


def build_identity() -> ModbusDeviceIdentification:
    identity = ModbusDeviceIdentification()
    identity.VendorName = "Home Assistant Modbus Gateway"
    identity.ProductCode = "HAGW"
    identity.VendorUrl = "https://www.home-assistant.io/"
    identity.ProductName = "Modbus TCP/RTU Gateway"
    identity.ModelName = "ModbusGateway"
    identity.MajorMinorRevision = "1.0"
    return identity


async def run_tcp(context, host, port, identity):
    logging.info("Starting Modbus TCP server on %s:%s", host, port)

    await StartAsyncTcpServer(
        context=context,
        identity=identity,
        address=(host, port),
    )


async def run_serial(
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
        "Starting Modbus RTU on %s baud=%s parity=%s stopbits=%s bytesize=%s timeout=%s",
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
    parser = argparse.ArgumentParser(description="Modbus TCP/RTU gateway")

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

    # 🔥 Enable verbose logging (including pymodbus internals)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
    )

    # Optional: turn on deep pymodbus debug
    logging.getLogger("pymodbus").setLevel(logging.DEBUG)

    context = build_context(args.register_count, args.unit_id)
    identity = build_identity()

    tasks = []

    if args.serial_enabled:
        tasks.append(
            run_serial(
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
        logging.info("Serial disabled")

    tasks.append(run_tcp(context, args.tcp_host, args.tcp_port, identity))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())