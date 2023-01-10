import queue, struct, threading
from time import sleep
from serial import *
from serial.tools import list_ports

# using can-passthrough!
class RovComms:
    HEADER = 0xA0
    FOOTER = 0x0B
    def __init__(self, on_orientation_chnage=[], on_accel_change=[], on_ang_chnage=[], on_quat_change=[], on_receive=[]):
        # on_receive are functions that are called when new data is available
        self.on_orientation = on_orientation_chnage
        self.on_accel = on_accel_change
        self.on_ang = on_ang_chnage
        self.on_quat = on_quat_change
        self.on_receive = on_receive
        
        self.orientation = [0, 0, 0]
        self.accel = [0, 0, 0]
        self.angular_rotation = [0, 0, 0]
        self.quaternion = [0, 0, 0, 0]

        self.device_found = False
        self.serial_comm = None
        self.serial_port = None

        self.read_thread = None
        self.write_thread = None

        self.read_queue = queue.Queue()
        self.write_queue = queue.Queue()

        # get the port with given device
        ports = list_ports.comports()
        for port in ports:
            if port.product == "Feather M4 CAN":
                self.serialPort = port
                device_found = True
                break
        
        if not device_found:
            # device not found, stop execution until found 8^(
            pass

        self.serial_comm = Serial(port=f"{self.serial_port}", baudrate=115200)
        self.start_threads()

    def read_loop(self):
        while True:
            buffer = []
            target_len = 0
            command = 0x00
            command_found = False
            header_found = False
            called_functions = []
            while True:
                if self.serial_comm.in_waiting > 0:
                    val = self.serial_comm.read()
                    if len(buffer) == 0 and val == RovComms.HEADER:
                        buffer.insert()
                        header_found = True
                    elif header_found and not command_found:
                        command = val
                        command_found = True
                        match val:
                            case 0x01:  # orientation
                                target_len = 2
                                called_functions = self.on_orientation_chnage
                            case 0x02:  # gyro
                                target_len = 2
                    elif command_found and header_found and len(buffer) < target_len:
                        buffer.insert(struct.unpack("=f", val))
                    elif len(buffer) == target_len:
                        # do stuff!
                        for function in called_functions:
                            function(buffer)
                        match command:
                            case 0x01:  # orientation
                                self.orientation = buffer[0:2]
                            case 0x02:  # gyro
                                self.angular_rotation = buffer[0:2]
                            case 0x03:  # accel
                                self.accel = buffer[0:2]
                            case 0x04:  # quat
                                self.quaternion = buffer[0:3]
       
    def write_loop(self):
        while True:
            if self.write_queue.not_empty:
                self.serial_comm.write(self.write_queue.get())

    def set_accelerations(self, accels):
        #acceleration in m/s, values in front, side, up, roll, pitch, yaw
        self.onshoreArduino.write(struct.pack("=ccffffffc", 0xA0, 0x01, accels[0], accels[1], accels[2], accels[3], accels[4], accels[5], 0x0B))
        # send_data = bytearray(7)
        # send_data[0] = 0x01
        # for i in range(6):
        #     send_data[1:4] = accels[i]
        
    def set_manual(self, thrusts):
        #manual thrust for each, percentage of thrust to each (same as accel) from -100 to 100
        self.onshoreArduino.write(struct.pack("=ccffffffc", 0xA0, 0x02, thrusts[0], thrusts[1], thrusts[2], thrusts[3], thrusts[4], thrusts[5], 0x0B))
    
    def start_threads(self):
        self.read_thread = threading.Thread(target=self.read_loop)
        self.write_thread = threading.Thread(target=self.write_loop)
        self.read_thread.start()
        self.write_thread.start()