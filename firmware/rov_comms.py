import queue, struct, threading
from time import sleep
from serial import *
from serial.tools import list_ports

# using can-passthrough!
class RovComms:
    HEADER = 0xA0.to_bytes(length=1, byteorder='big', signed=False)
    FOOTER = 0x0B.to_bytes(length=1, byteorder='big', signed=False)
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
        self.pidErrors = [0, 0, 0, 0, 0, 0]

        self.device_found = False
        self.angular_rotation = [0, 0, 0]
        self.quaternion = [0, 0, 0, 0]
        self.pidErrors = [0, 0, 0, 0, 0, 0]

        self.device_found = False
        self.serial_port = None

        self.read_thread = None
        self.write_thread = None

        self.read_queue = queue.Queue()
        self.write_queue = queue.Queue()
        
        while not self.device_found:
            # get the port with the given device
            ports = list_ports.comports()
            for port in ports:
                # print(port.product)
                # print(port.)
                if port.product == "Feather M4 CAN":
                    self.serial_port = port.device
                    self.device_found = True
                    break
            # device not found, continue until found
            sleep(0.1)

        self.serial_comm = Serial(port=f"{self.serial_port}", baudrate=115200)
        self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
        self.write_thread = threading.Thread(target=self.write_loop, daemon=True)
        self.read_thread.start()
        self.write_thread.start()

    def read_loop(self):
        # while True:
        #     if self.serial_comm.in_waiting > 0:
        #         print(self.serial_comm.read(), sep="")
        # print('a')


        while True:
            # print("read data~")
            buffer = bytearray()
            data = 0
            target_len = 0
            curr_index = 0
            command = 0x00
            header_found = False
            called_functions = []
            while True:
                if self.serial_comm.in_waiting > 0:
                    # print("reading")
                    val = self.serial_comm.read()
                    # print(type(val))
                    if not header_found:
                        # print("found header")
                        if val == RovComms.HEADER:
                            header_found = True
                            curr_index += 1
                    elif curr_index == 1:
                        # print("found command")
                        command = int.from_bytes(val, "big")
                        match command:
                            case _:
                                target_len = 4
                        curr_index += 1
                    elif curr_index-2 < target_len:
                        # print("reading")
                        # print(buffer)
                        buffer += val
                        # print(buffer)
                        curr_index += 1

                        # match val:
                        #     case 0x01:  # orientation
                        #         target_len = 2
                        #         called_functions = self.on_orientation_chnage
                        #     case 0x02:  # gyro
                        #         target_len = 2
                    else:
                        # do stuff!
                        # print('a')
                        # print(buffer)
                        data = (struct.unpack("=f", buffer))[0]
                        # print(data)
                        for function in called_functions:
                            function(buffer)
                        data_index = (command & 0b00011)
                        match (command >> 2):
                            case 0x00:  # orientationa
                                if data_index in [0, 1, 2]:
                                    self.orientation[data_index] = data
                            case 0x01:  # gyro
                                if data_index in [0, 1, 2]:
                                    self.angular_rotation[data_index] = data
                            case 0x02:  # accel
                                if data_index in [0, 1, 2]:
                                    self.accel[data_index] = data
                            case 0x03:  # quat
                                if data_index in [0, 1, 2, 3]:
                                    self.quaternion[data_index] = data
                            case 0x05:
                                if data_index in [0, 1, 2]:
                                    self.pidErrors[data_index] = data
                                    print("f error: ")
                            case 0x06:
                                if data_index in [0, 1, 2]:
                                    self.pidErrors[data_index+3] = data
                        curr_index = 0
                        header_found = False
                        target_len = 0
                        break
       

    def write_loop(self):
        while True:
            if self.write_queue.not_empty:
                self.serial_comm.write(self.write_queue.get())
            # sleep(0.01)

    def set_accelerations_thrust(self, accels):
        # acceleration in m/s, values in front, side, up, roll, pitch, yaw
        self.write_queue.put(struct.pack("=ccffffffc", RovComms.HEADER, 0x1A.to_bytes(length=1, byteorder='big', signed=False), float(accels[0]), float(accels[1]), float(accels[2]), float(accels[3]), float(accels[4]), float(accels[5]), RovComms.FOOTER))
        # send_data = bytearray(7)
        # send_data[0] = 0x01
        # for i in range(6):
        #     send_data[1:4] = accels[i]
        
    def set_manual_thrust(self, thrusts):
        # manual thrust for each, percentage of thrust to each (same as accel) from -100 to 100
        self.write_queue.put(struct.pack("=ccffffffc", RovComms.HEADER, 0x1B.to_bytes(length=1, byteorder='big', signed=False), float(thrusts[0]), float(thrusts[1]), float(thrusts[2]), float(thrusts[3]), float(thrusts[4]), float(thrusts[5]), RovComms.FOOTER))
        print("finished")

    def move_camera_servo(self, servo_num, degree):
        # degree is int, servo_num is byte
        self.write_queue.put(struct.pack("=ccicc", RovComms.HEADER, 0x20.to_bytes(length=1, byteorder='big', signed=False), int(degree), servo_num.to_bytes(length=1, byteorder="big", signed=False), RovComms.FOOTER))
        print(struct.calcsize("=ic"))

    def change_pid(self, movement, constant, new_value):
        num_constant = 0
        if constant == 'p':
            num_constant = 0
        elif constant == 'i':
            num_constant = 1
        elif constant == 'd':
            num_constant = 2
        num_constant = int(num_constant).to_bytes(length=1, byteorder="big", signed=False)
        movement = int(movement).to_bytes(length=1, byteorder="big", signed=False)
        self.write_queue.put(struct.pack("=ccccfc", RovComms.HEADER, 0x02.to_bytes(length=1, byteorder='big', signed=False), movement, num_constant, new_value, RovComms.FOOTER))
        

if __name__ == "__main__":
    comms = RovComms()
    while True:
        val = input()
        deg = input()
        match val:
            case 'a':
                print('A')
                comms.set_manual_thrust([float(deg), 0, 0, 0, 0, 0])
            case ' ':
                comms.set_manual_thrust([0, 0, 0, 0, 0, 0])
            case 'q':
                comms.set_manual_thrust([0, float(deg), 0, 0, 0, 0])
            case 'i':
                comms.set_manual_thrust([0, 0, float(deg), 0, 0, 0])
            case 'w':
                comms.move_camera_servo(0, int(deg))
            case '1':
                comms.set_accelerations_thrust([0, 0, 0, 90, 0, 0])
            case '2':
                comms.change_pid(movement=1, constant=0, new_value=1)
            case '3':
                print(comms.orientation)
                print(comms.pidErrors)
            case _:
                print(comms.orientation)
                print(comms.accel)
                print(comms.angular_rotation)
                print(comms.quaternion)