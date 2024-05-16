import serial
import time
import serial.tools.list_ports as ports_list

available_ports = []

class ot_device:
    def __init__(self, port):
        self.port = port  # COM Port
        self.serial = serial.Serial(
            self.port, 38400, timeout=0, parity=serial.PARITY_EVEN
        )
        self.platform = "" #zephyr or efr32

    # Safely open port only if not open
    def open_port(self):
        if not self.serial.is_open:
            self.serial.open()

    # Safely close port only if open
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
        print("\n" + str(len(ports_l)) + " serial devices found:")
        for p in ports_l:
            print(p)
    return ports_l

def find

if __name__ == "__main__":
    available_ports = get_ports()