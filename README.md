# twc3-addon

This repository contains one or more Home Assistant add-ons.

A root-level `repository.yaml` is provided so Home Assistant can recognize this repository as an app/add-on repository. The add-on itself lives in the `modbus-gateway/` subdirectory.

## Add-ons

- `modbus-gateway/` - Modbus TCP / RS485 gateway add-on

## Usage

Add this repository to Home Assistant Supervisor as a custom add-on repository using:

`https://github.com/pnousiai/twc3-addon`

Then install the add-on from the `modbus-gateway` directory.
