import os
import sys
import glob
import serial
import serial.tools.list_ports as ports_list

ports = []


def get_ports():
    ports_l = list(ports_list.comports())
    for p in ports_l:
        print(p)
    return ports_l


if __name__ == "__main__":
    ports = get_ports()
