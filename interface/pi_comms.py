# import RPi.GPIO as GPIO
import socket, select, queue, threading, struct
from collections import namedtuple

import sys
from pathlib import Path
path = Path(sys.path[0])
sys.path.insert(1, str((path.parent.parent.parent).absolute()))

from interface_utils import *

class PIClient:
    #code to communicate to opi
    move = namedtuple("move", ['f', 's', 'u', 'p', 'r', 'y'])
    def __init__(self, server_address=("192.168.13.101", 27777)):
        self.out_queue = queue.Queue()
        self.client_thread = threading.Thread(target=self.client_loop, args=[server_address], daemon=True)
        self.client_thread.start()
        self.sens_data = SensorData()
    
    def client_loop(self, server_address):
        while True:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # self.sock.connect(address)
            self.sock.sendto(0x10.to_bytes(length=1, byteorder='big', signed=False), server_address) #try to connect
            print("client sent attempt to connect")
            while True:
                r, w, x = select.select([self.sock], [self.sock], [self.sock])
                for sock in r:  #ready to read!
                    print("received data")
                    self.process_data(sock.recv(2048))
                
                for sock in w:  #ready to write!
                    if not self.out_queue.empty():
                        sock.sendto(self.out_queue.get(), server_address)
                        print("wrote data")
                
                for sock in x:  #exception 8^(. Create new socket and try to connect again.
                    print("exception in networking")

    def process_data(self, pkt):
        print(pkt)
        # turn into packet
        cmd = pkt[0]
        param = pkt[1]
        len = pkt[2]
        temp = []
        for i in range(len):
            temp.append(pkt[i+3])
        data = temp
        # your wish for match has been fulfilled
        match(cmd):
            case 0x00:
                # echo or hello
                self.sens_data.other = bytes(data).decode('latin')
                print(self.sens_data.other)
            case 0x0A:
                # get system attribute
                if not data:
                    return
                self.sens_data.system.sys_enable = data[0]
            case 0x0F:
                # success
                if not data:
                    self.sens_data.system.failed = 1
                    return
                self.sens_data.system.failed = data[0]
            case 0x1A:
                # thruster positions
                if len == 2 and THRUSTER_ONE <= param <= THRUSTER_SIX:
                    self.sens_data.outputs.update(param, struct.unpack('!H', data)[0])
                if len == 12 and param == THRUSTER_ALL:
                    self.sens_data.outputs.update_all_thrusters(struct.unpack('!HHHHHH', data))
            case 0x2A:
                # servo positions
                if len == 2 and SERVO_LEFT <= param <= SERVO_RIGHT:
                    self.sens_data.outputs.update(param, struct.unpack('!H', data)[0])
                if len == 4 and param == SERVO_ALL:
                    self.sens_data.outputs.update_all_servos(struct.unpack('!HH', data))
            case 0x33:
                # some type of sensor data
                new_data = None
                if len == 2:
                    new_data = struct.unpack('!H', data)[0]
                elif len == 4:
                    new_data = struct.unpack('!f', data)[0]
                elif len == 12:
                    new_data = Vector3.from_arr(struct.unpack('!fff', data))
                elif len == 16:
                    new_data = Quaternion.from_arr(struct.unpack('!ffff', data))

                # make sure type is correct
                if param in SENSOR_TYPES:
                    assert type(new_data) == SENSOR_TYPES[param], f"wrong type for packet type {param}, expected {SENSOR_TYPES[param]}, got {type(new_data)}"
                else:
                    print("?????????")

                # every possible ..
                if param == SENSOR_ACCEL:
                    self.sens_data.accel = new_data
                elif param == SENSOR_MAG:
                    self.sens_data.mag = new_data
                elif param == SENSOR_GYRO:
                    self.sens_data.gyro = new_data
                elif param == SENSOR_EULER:
                    self.sens_data.orientation = new_data
                elif param == SENSOR_QUATERNION:
                    self.sens_data.quaternion = new_data
                elif param == SENSOR_LINACCEL:
                    self.sens_data.linaccel = new_data
                elif param == SENSOR_GRAVITY:
                    self.sens_data.gravity = new_data
                elif param == SENSOR_CALIBRATION:
                    self.sens_data.status.calib_sys = new_data & 0b11000000
                    self.sens_data.status.calib_gyr = new_data & 0b00110000
                    self.sens_data.status.calib_acc = new_data & 0b00001100
                    self.sens_data.status.calib_mag = new_data & 0b00000011
                elif param == SENSOR_SYSTEM:
                    self.sens_data.status.sys_status = new_data & 0xFF00
                    self.sens_data.status.sys_err    = new_data & 0x00FF
                elif param == SENSOR_TEMP:
                    self.sens_data.temperature = new_data

    def move_claw(self, claw_num, claw_deg):
        assert isinstance(claw_num, int), "claw_num must be an int specifying the selected claw"
        assert isinstance(claw_deg, int), "claw_deg must be an int specifying the degree to write to the selected claw"
        # assert claw_deg <= 2000 and claw_deg >= 1000, "claw deg must be between 1000 and 2000"
        assert claw_num >= 0 and claw_num <= 1, "claw_num must be 0 or 1" 
        self.out_queue.put(struct.pack("!ccH", bytes([0x20, claw_num]), claw_deg))

    def turn_flashlight_off(self):
        self.out_queue.put(struct.pack("!cc", bytes([0x30, 0x00])))

    def turn_flashlight_on(self):
        self.out_queue.put(struct.pack("!cc", bytes([0x30, 0x01])))
    
    def set_pid_thrust(self, thrusts):
        pass

    def set_manual_thrust(self, moves):
        assert isinstance(moves, list), "thrusts must be an array of floats"
        assert len(moves) == 6, "thrusts must be 6 long"
        # print(thrusts[1])
        # self.out_queue.put(struct.pack("!cHHHHHHHH"), thrusts_int[0], thrusts_int[1], thrusts_int[2])
        self.out_queue.put(struct.pack("!cfff", bytes([0x00]), *(moves[0:3])))
        self.out_queue.put(struct.pack("!cfff", bytes([0x04]), *(moves[3:])))

    def set_pos_manual(self, moves):
        self.out_queue.put(struct.pack("!cfff", bytes([0x00]), *moves))
    
    def set_rot_manual(self, moves):
        self.out_queue.put(struct.pack("!cfff", bytes([0x04]), *moves))

    def set_pos_pid(self, target_vel):
        self.out_queue.put(struct.pack("!cfff", bytes([0x01]), *target_vel))
    
    def set_rot_angle(self, target_eul):
        self.out_queue.put(struct.pack("!cfff", bytes([0x05]), *target_eul))
    
    def set_rot_vel(self, target_vel):
        self.out_queue.put(struct.pack("!cfff", bytes([0x06]), *target_vel))

    def test_connection(self):
        self.out_queue.put(struct.pack("!c", bytes([0x10])))

if __name__ == "__main__":
    addr = str(input("enter server address> "))
    comms = PIClient((addr, 7772))
    while True:
        command = input()
        match(command):
            case "bruh":
                comms.test_connection()
            case 'tt':
                comms.set_manual_thrust([1, 0, 0, 0, 0, 0])
            case 'stop':
                comms.set_manual_thrust([0, 0, 0, 0, 0, 0])
            case 'tf':
                comms.set_manual_thrust([0.2, 0, 0, 0, 0, 0])
            case 'ts':
                comms.set_manual_thrust([0, 0.2, 0, 0, 0, 0])
            case 'tu':
                comms.set_manual_thrust([0, 0, 0.2, 0, 0, 0])
            case 's1':
                comms.move_claw(0, int(input()))
            case 's0':
                comms.move_claw(1, int(input()))
            case 'on':
                comms.turn_flashlight_on()
            case 'off':
                comms.turn_flashlight_off()
            case "lel":
                thrust = input(">")
                comms.set_manual_thrust([float(thrust), 0, 0, 0, 0, 0])
