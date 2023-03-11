from abc import ABC, abstractmethod, abstractproperty
from typing import Union
import serial
import struct
from queue import Queue
import threading
from utils import *
from firmware.v3.main_tube.mcu_utils import *
from firmware.v3.main_tube.mcu_constants import *


class MCUInterface(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def send_bytes(self, data: bytes):
        pass

    @abstractmethod
    def send_data(self, data: Union[list[Union[int, str]], str]):
        pass


class UARTMCUInterface(MCUInterface):
    def __init__(self, port, net_out_queue):
        # create the serial object with no port since we do not want to connect
        self.ser = serial.Serial(None, 115200)
        self.ser.port = port
        self.write_thread = threading.Thread(target=self._write)
        self.write_queue = Queue()  # of Packets
        self.read_thread = threading.Thread(target=self._read)
        self.build_packet = IncompletePacket()
        self.enable_signal = Signal(False)
        self.data = SensorData()
        self.net_out_queue = net_out_queue

    def _write(self):
        while self.enable_signal.enabled:
            if self.write_queue.not_empty:
                # pkt: Packet = self.write_queue.get_nowait()
                pkt : Packet = self.write_queue.get()
                if pkt:
                    print(pkt)
                    self.ser.write(pkt.bytes)    #WRITE IS BIG ENDIAN!!!!

    def _read(self):
        while self.enable_signal.enabled:
            new_bytes = self.ser.read_all()
            for byte in new_bytes:
                self.build_packet.add_byte(byte)
                print(self.build_packet)
                if self.build_packet.is_complete():
                    print("parsing")
                    self._parse(self.build_packet.to_packet())  # read is LITTLE ENDIAN!!!!
                    self.build_packet.clear()

    def _parse(self, packet: Packet):
        print("received serial data")
        print(packet)
        self.net_out_queue.put(packet.to_network_packet())

    def start(self):
        self.enable_signal.enabled = True
        if not self.ser.is_open:
            self.ser.open()
        self.write_thread.start()
        self.read_thread.start()

    def stop(self):
        self.enable_signal.enabled = False
        if self.ser.is_open:
            self.ser.close()
        self.write_thread.join()
        self.read_thread.join()

    def send_bytes(self, data: bytes):
        print(data)
        self.ser.write(data)

    # replaced by new version (does not use packets!)
    # def send_packet(self, command: int, param: int, length: int, data: bytes):
    #     # to_lrc = bytes([command, param, length]) + bytes(data)
    #     # lrc = LRC(to_lrc)
    #     print(f"sending packet: command: {command}, param: {param}, length: {length}, data: {data}")
    #     # trmt = bytes([HEADER_TRMT, command, param, length]) + bytes(data) + bytes(FOOTER_TRMT)
    #     print(type(data))
    #     trmt = bytes([HEADER_TRMT, command, param, length]) + data + bytes([FOOTER_TRMT])

        # self.send_bytes(trmt)

    def send_packet(self, command: int, param: int, length: int, data: tuple):
        self.write_queue.put(Packet(command, param, [i[0] for i in data]))
        # self.send_bytes(struct.pack(">BBBB", HEADER_TRMT, command, param, length))

        # if length:
        #     byte_type = ">" + "B" * length
        #     self.send_bytes(struct.pack(byte_type, *[ord(i) for i in [*data]]))

        # self.send_bytes(struct.pack(">B", FOOTER_TRMT))

    def send_data(self, data: Union[list[Union[int, str]], str]):
        if type(data) == str:
            self.send_bytes(str.encode('latin'))
            return
        if data:
            if type(data[0]) == str:
                self.send_bytes(bytes("".join(data), 'latin'))
            elif type(data[0]) == int:
                self.send_bytes(bytes(data))
