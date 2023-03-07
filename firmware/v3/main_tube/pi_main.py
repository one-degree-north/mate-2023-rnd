import queue
# from utils import *
from mcu_utils import *
from mcu_constants import *
from interface import UARTMCUInterface
from pi_server import *
from time import sleep

# import sys, os
# from pathlib import Path
# path = Path(sys.path[0])
# sys.path.insert(1, str((path.parent.parent.parent).absolute()))

if __name__ == "__main__":
    addr = str(input("enter server address: "))
    server_address = (addr, 7772)
    serial_port = str(input("enter serial port"))
    port = serial_port
    out_queue = queue.Queue()
    mcu = UARTMCUInterface(port, out_queue)
    # mcu.start()
    print(type(mcu))
    pi_s = PIServer(server_address=server_address, mcu=mcu, out_queue=out_queue)
    mcu.start()
    print("AAA")
    while True:
        sleep(10)