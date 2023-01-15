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
        
        while not device_found:
            # get the port with the given device
            ports = list_ports.comports()
            for port in ports:
                if port.product == "Feather M4 CAN":
                    self.serialPort = port
                    device_found = True
                    break
            # device not found, continue until found
            sleep(0.1)

        self.serial_comm = Serial(port=f"{self.serial_port}", baudrate=115200)
        self.read_thread = threading.Thread(target=self.read_loop)
        self.write_thread = threading.Thread(target=self.write_loop)
        self.read_thread.start()
        self.write_thread.start()

    def read_loop(self):
        while True:
            buffer = []
            data = 0
            target_len = 0
            curr_index = 0
            command = 0x00
            header_found = False
            called_functions = []
            while True:
                if self.serial_comm.in_waiting > 0:
                    val = self.serial_comm.read()
                    if not header_found:
                        if val == RovComms.HEADER:
                            header_found = True
                            curr_index += 1
                    elif curr_index == 1:
                        command = val
                        match command:
                            case _:
                                target_len = 4
                    elif curr_index <= target_len:
                        buffer.insert(val)


                        # match val:
                        #     case 0x01:  # orientation
                        #         target_len = 2
                        #         called_functions = self.on_orientation_chnage
                        #     case 0x02:  # gyro
                        #         target_len = 2
                    else:
                        # do stuff!
                        data = struct.pack("=f", buffer)
                        for function in called_functions:
                            function(buffer)
                        data_index = (command & 0b00011)
                        match (command >> 2):
                            case 0x01:  # orientation
                                if data_index in [0, 1, 2]:
                                    self.orientation[data_index] = data
                            case 0x02:  # gyro
                                if data_index in [0, 1, 2]:
                                    self.angular_rotation[data_index] = data
                            case 0x03:  # accel
                                if data_index in [0, 1, 2]:
                                    self.accel[data_index] = data
                            case 0x04:  # quat
                                if data_index in [0, 1, 2, 3]:
                                    self.quaternion[data_index] = data
       
    def write_loop(self):
        while True:
            if self.write_queue.not_empty:
                self.serial_comm.write(self.write_queue.get())
            # sleep(0.01)

    def set_accelerations_thrust(self, accels):
        #acceleration in m/s, values in front, side, up, roll, pitch, yaw
        self.onshoreArduino.write(struct.pack("=ccffffffc", RovComms.HEADER, 0x1A, accels[0], accels[1], accels[2], accels[3], accels[4], accels[5], RovComms.FOOTER))
        # send_data = bytearray(7)
        # send_data[0] = 0x01
        # for i in range(6):
        #     send_data[1:4] = accels[i]
        
    def set_manual_thrust(self, thrusts):
        #manual thrust for each, percentage of thrust to each (same as accel) from -100 to 100
        self.onshoreArduino.write(struct.pack("=ccffffffc", RovComms.HEADER, 0x1B, thrusts[0], thrusts[1], thrusts[2], thrusts[3], thrusts[4], thrusts[5], RovComms.FOOTER))