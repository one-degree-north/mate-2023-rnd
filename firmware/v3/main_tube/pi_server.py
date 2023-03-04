# import RPi.GPIO as GPIO
import socket, select, queue, struct, threading
from utils import *
from firmware.v3.main_tube.mcu_utils import *
from firmware.v3.main_tube.mcu_constants import *
from firmware.v3.main_tube.interface import *

class PIServer:
    MAX_THRUST_PERCENT = 70 # max in thrust percent
    MIN_THRUST_PERCENT = 5 #mininum thrust, if lower, automatically go to minimum
    CENTER_THRUST = 1400    # center in milliseconds
    MAX_RANGE = 400 # maximum difference in milliseconds
    MAX_THRUST = CENTER_THRUST + MAX_RANGE * MAX_THRUST_PERCENT / 100.0
    MIN_THRUST = CENTER_THRUST - MAX_RANGE * MAX_THRUST_PERCENT / 100.0
    #code for opi server
    def __init__(self, server_address: tuple, mcu, out_queue: queue.Queue):
        self.connected = False
        self.out_queue = out_queue
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(server_address)
        self.self_addr = server_address
        self.mcu = mcu
        print(f"server set up at {server_address}")
        self.client_addr = ()
        self.server_thread = threading.Thread(target=self.server_loop, daemon=True)
        self.server_thread.start()

    def server_loop(self):
        while True:
            r, w, x = select.select([self.sock], [self.sock], [self.sock])
            for sock in r:  #ready to read!
                print("attempting to read")
                data, address = sock.recvfrom(2048)
                if address != self.client_addr: #client switched address (something wrong happened)
                    self.client_addr = address
                self._parse_data(data, address)
                print("received data")
            
            for sock in w:  #ready to write!
                # print("attempting to write")
                if not self.out_queue.empty() and self.connected:
                    print("attempting to write")
                    sock.sendto(self.out_queue.get(), self.client_addr)
                    print("wrote data")
            
            for sock in x:  #exception 8^(. Create new socket and try to connect again.
                print("exception apparently")
                pass
            # events = self.poller.poll()
            # for sock, event in events:
            #     if event & select.POLLIN:   # can write data!
            #         data, address = sock.recvfrom(2048)
            #         print("server received data to process")
            #         self.process_data(data, address)
            #     if event & (select.POLLOUT | select.POLLPRI) and not self.out_queue.empty() and self.connected:    # can read data!
            #         sock.sendto(self.out_queue.get())  # WE SHOULDN'T BE SENDING DATA RIGHT NOW!
            #         print("server sent data?")
            #     if event & (select.POLLHUP | select.POLLERR): # problem with communications, disconnect client and try to find new one
            #         # not sure when this would happend with udp...
            #         self.connected = False
            #         print("server ERROR, disconnected")
            #         break
    
    def _parse_data(self, data, address):
        self.connected = True
        self.client_addr = address
        cmd = data[0]
        vals = data[1:]
        print(f"received data from {address} with command: {cmd}, datalen: {len(data)}")
        match (cmd):
            case 0x00:  #test communications
                self.mcu.send_packet(0x00, 0x00, 0x00, bytes([]))
            case 0x01:  #move thrusters
                # pass
                if len(vals) == 16:
                    thrusts = struct.unpack("!HHHHHHHH", vals)
                    self.mcu.send_packet(0x18, 0x08, 0x08, thrusts)
                    print(f"moving with thrusts {thrusts}")
            case 0x02:  #move servos
                pass
            case 0x03:  #toggle flashlight
                pass
            case 0x10:  #data autoreport
                pass


if __name__ == "__main__":
    comms = PIServer(("127.0.0.1", 7772))