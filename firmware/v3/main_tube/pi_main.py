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
    server_address = ("127.0.0.1", 7772)
    port = "/dev/ttyUSB0"
    out_queue = queue.Queue()
    mcu = UARTMCUInterface(port, out_queue)
    print(type(mcu))
    pi_s = PIServer(server_address=server_address, mcu=mcu, out_queue=out_queue)
    print("AAA")
    while True:
        sleep(10)