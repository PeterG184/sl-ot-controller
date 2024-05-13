import serial
import time
import serial.serialutil
import serial.tools.list_ports as ports_list

available_ports = []
devices = []


class ot_device:
    def __init__(self, port):
        self.port = port
        self.serial = serial.Serial(
            self.port, 38400, timeout=0, parity=serial.PARITY_EVEN
        )

    def open_port(self):
        if not self.serial.is_open:
            self.serial.open()

    def close_port(self):
        if self.serial.is_open:
            self.serial.close()

    def run_command(self, command):
        self.serial.write(command + b"\r\n")
        time.sleep(0.1)
        return self.get_output(command)

    def get_output(self, command):
        res = self.serial.read_all()
        res = res.decode()
        return command.decode() + ": " + res.replace(command.decode(), '').replace('>', '').replace('\r', '').replace('\n', ' ')


def get_ports():
    ports_l = list(ports_list.comports())
    if len(ports_l):
        print("\n" + str(len(ports_l)) + " available devices found:")
        for p in ports_l:
            print(p)
    return ports_l


def link_devices():
    for port in available_ports:
        if port.name[:3].lower() == "com":
            device = ot_device(port.name)
            devices.append(device)


if __name__ == "__main__":
    available_ports = get_ports()
    link_devices()
    for device in devices:
        print(device.run_command(b"ifconfig up"))
        print(device.run_command(b"thread start"))
        print(device.run_command(b"state"))
