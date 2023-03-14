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
    def __init__(self):
        self.clear()

    def add_byte(self, byte):
        byte &= 0xFF
        if self.curr_size == 0: # header
            if byte == HEADER:
                self.curr_size += 1
            else:
                return False
            self.header = byte
        elif self.curr_size == 1: # cmd
            self.cmd = byte
            self.curr_size += 1
        elif self.curr_size == 2: # param
            self.param = byte
            self.curr_size += 1
        elif self.curr_size == 3: # len
            self.len = byte
            self.curr_size += 1
        elif self.curr_size > 3 and self.curr_size <= 3+self.len: # data
            self.data[self.curr_size-4] = byte
            self.curr_size += 1
        elif self.curr_size == 4+self.len:
            if byte == FOOTER: # we're done!
                self.complete = True
            else:
                self.clear()
        else:   #??????
            print("somehow got out of curr_size")
            self.clear()
            return False
        return True

    def clear(self):
        self.header=self.cmd=self.param=self.len=self.footer=-1
        self.data = []
        self.complete = False
        self.curr_size = 0
    
    def is_complete(self):
        return self.complete

class MCUInterface:
    def __init__(self, port):
        self.ser = serial.Serial(None, 115200)
        self.ser_enabled = False
        self.read_packet = Packet()
    
    def start(self):
        self.ser_enabled = True
        if not self.ser.is_open:
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

    def _parse(self):
        pass

    def set_thrusters(self, thrusts):
        self._write_packet(0x18, 0x0F, struct.pack(">HHHHHHHH", *thrusts))