import serial
import time
import serial.tools.list_ports as ports_list

# List of available ports
available_ports = []
# List of devices that the CLI is connected to
devices = []


class ot_device:
    def __init__(self, port):
        self.port = port  # COM Port
        self.serial = serial.Serial(
            self.port, 38400, timeout=0, parity=serial.PARITY_EVEN
        )

    # Open port if not open
    def open_port(self):
        if not self.serial.is_open:
            self.serial.open()

    # Close port if open
    def close_port(self):
        if self.serial.is_open:
            self.serial.close()

    # Run command and wait 10ms and return formatted output
    def run_command(self, command):
        self.serial.write(command + b"\r\n")
        time.sleep(0.01)
        return self.get_output(command)

    # Get output and format lines
    def get_output(self, command):
        res = self.serial.read_all()
        res = res.decode()
        return (
            res.replace(command.decode(), "")
            .replace(">", "")
            .replace("\r", "")
            .replace("\n", " ")
        )


# Get available COM ports
def get_ports():
    ports_l = list(ports_list.comports())
    if len(ports_l):
        print("\n" + str(len(ports_l)) + " available devices found:")
        for p in ports_l:
            print(p)
    return ports_l


# Create device object for each available port
def link_devices():
    for port in available_ports:
        if port.name[:3].lower() == "com":
            device = ot_device(port.name)
            devices.append(device)


# Execute command on each device
def handle_command(command):
    response_dict = {}
    for device in devices:
        response = device.run_command(command)
        # Add response to dictionary, where setup is {response: [device ids]}
        try:
            response_dict[response].append(device.port)
        except:
            response_dict[response] = [device.port]
    return response_dict


# CLI interface loop
def interface():
    while True:
        command = input(">")
        response = handle_command(command.encode())
        for res in response:
            print(res + " | " + (' ').join(response[res]))


if __name__ == "__main__":
    available_ports = get_ports()
    link_devices()
    interface()
