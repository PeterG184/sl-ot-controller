## Command Line Interface for Silicon Labs Devices ##
This is a CLI for interacting with and operating multiple silicon labs open thread enabled devices at once.

### Requirements ###
 - [PySerial](https://pypi.org/project/pyserial/)
 - Silicon Labs device running OpenThread CLI (instructions available [here](https://github.com/PeterG184/ot-ftd-cli-silicon-labs))

### Usage ###
Running the program will scan all available serial devices, and any command entered will run on all devices. All responses will be captured and returned.
