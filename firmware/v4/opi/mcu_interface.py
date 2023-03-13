# mcu_interface communicates with the microcontroller
from dataclasses import dataclass
import serial, struct

HEADER = 0xa7
FOOTER = 0x7a

@dataclass
class Packet:
    cmd: int
    param: int
    len: int
    data: list[int]
    curr_size: int
    complete: bool
    all_bytes: bytes
    def __init__(self):
        self.clear()

    def add_byte(self, byte):
        byte &= 0xFF
        if self.curr_size == 0: # header
            if byte != HEADER:
                return False
            self.header = byte
        elif self.curr_size == 1: # cmd
            self.cmd = byte
        elif self.curr_size == 2: # param
            self.param = byte
        elif self.curr_size == 3: # len
            self.len = byte
        elif self.curr_size > 3 and self.curr_size <= 3+self.len: # data
            self.data[self.curr_size-4] = byte
        elif self.curr_size == 4+self.len:
            if byte == FOOTER: # we're done!
                self.complete = True
                return True
            else:
                self.clear()
                return False
        else:   #??????
            print("somehow got out of curr_size")
            self.clear()
            return False
        self.all_bytes += bytes(byte)
        self.curr_size += 1
        return True
    
    def to_bytes(self):
        return self.all_bytes

    def clear(self):
        self.header=self.cmd=self.param=self.len=self.footer=-1
        self.data = []
        self.complete = False
        self.curr_size = 0
        self.all_bytes = []
    
    def is_complete(self):
        return self.complete

class MCUInterface:
    def __init__(self, port, server):
        self.ser = serial.Serial(None, 115200)
        self.ser_enabled = False
        self.read_packet = Packet()
        self.server = None
    
    def set_server(self, server):
        self.server = server

    def start(self):
        self.ser_enabled = True
        if not self.ser.is_open and self.server != None:
            self.ser.open()
        self.write_thread.start()
        self.read_thread.start()

    def _write_packet(self, cmd:int, param:int, data): #WRITE IS BIG ENDIAN!!!!
        self.ser.write(struct.pack(">BBBB", HEADER, cmd, param, len(data)) + data + struct.pack(">B", FOOTER))

    def _read_thread(self): #READ IS LITTLE ENDIAN!!!!!
        while True:
            new_bytes = self.ser.read_all()
            for byte in new_bytes:
                self.read_packet.add_byte(byte)
                if self.read_packet.is_complete():
                    self._parse(self.read_packet)  # read is LITTLE ENDIAN!!!!
                    self.read_packet.clear()

    # parse data, stores data needed on opi and sends data to surface
    def _parse(self, packet):
        # store data needed

        # forward to network
        pkt_len = len(packet.to_bytes())
        self.server.send_data(struct.pack("!" + "B"*pkt_len, *struct.unpack("<" + "B"*pkt_len, packet.to_bytes())))    # transform little endian into network endianess

    def set_thrusters(self, thrusts):
        self._write_packet(0x18, 0x0F, struct.pack(">HHHHHHHH", *thrusts))