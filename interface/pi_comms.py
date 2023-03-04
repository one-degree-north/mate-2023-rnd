# import RPi.GPIO as GPIO
import socket, select, queue, threading, struct
from collections import namedtuple

class PIClient:
    #code to communicate to opi
    move = namedtuple("move", ['f', 's', 'u', 'p', 'r', 'y'])
    MAX_THRUST_PERCENT = 70 # max in thrust percent
    MIN_THRUST_PERCENT = 5 #mininum thrust, if lower, automatically go to minimum
    CENTER_THRUST = 1400    # center in milliseconds
    MAX_RANGE = 400 # maximum difference in milliseconds
    MAX_THRUST = int(CENTER_THRUST + MAX_RANGE * MAX_THRUST_PERCENT / 100.0)
    MIN_THRUST = int(CENTER_THRUST - MAX_RANGE * MAX_THRUST_PERCENT / 100.0)
    REVERSE_THRUSTS = [False, True, False, False, False, True, True, False]
    def __init__(self, server_address=("192.168.13.101", 27777)):
        self.out_queue = queue.Queue()
        self.client_thread = threading.Thread(target=self.client_loop, args=[server_address], daemon=True)
        self.client_thread.start()
    
    def client_loop(self, server_address):
        while True:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # self.sock.connect(address)
            self.sock.sendto(0x00.to_bytes(length=1, byteorder='big', signed=False), server_address) #try to connect
            print("client sent attempt to connect")
            while True:
                r, w, x = select.select([self.sock], [self.sock], [self.sock])
                for sock in r:  #ready to read!
                    self.process_data(sock.recv(2048))   #THERE SHOULDN'T BE DATA BEING RECEVIED AS OF NOW!
                    print("received data")
                
                for sock in w:  #ready to write!
                    if not self.out_queue.empty():
                        sock.sendto(self.out_queue.get(), server_address)
                        print("wrote data")
                
                for sock in x:  #exception 8^(. Create new socket and try to connect again.
                    break

    def process_data(self, data):
        pass

    def set_manual_thrust_test(self, thrusts, verticle_thrust_adjustments=[0, 0, 0, 0]):
        assert isinstance(thrusts, list), "thrusts must be an array of floats"
        assert len(thrusts) == 6, "thrusts must be array of 6 floats"
        assert len(verticle_thrust_adjustments) == 4, "only 4 verticle thrusters"
        for i in range(len(thrusts)):
            try:
                thrusts[i] = float(thrusts[i])
            except ValueError:
                assert False, "data in thrusts must be float"
            assert thrusts[i] < 100 and thrusts[i] > -100, "data in thrusts must be float between -100 and 100"
        thrust_vals = [0, 0, 0, 0, 0, 0, 0, 0]  #thruster values in percentages (directly written), will be changed to milliseconds
        mov = PIClient.move(*thrusts)
        # forward / side thrusters
        thrust_vals[7] = mov.f - mov.s - mov.y
        thrust_vals[2] = mov.f + mov.s + mov.y
        thrust_vals[0] = mov.f - mov.s + mov.y
        thrust_vals[6] = mov.f + mov.s - mov.y
        # up thrusters
        thrust_vals[5] = mov.u + mov.p - mov.r + verticle_thrust_adjustments[0]
        thrust_vals[3] = mov.u + mov.p + mov.r + verticle_thrust_adjustments[1]
        thrust_vals[1] = mov.u - mov.p + mov.r + verticle_thrust_adjustments[2]
        thrust_vals[4] = mov.u - mov.p - mov.r + verticle_thrust_adjustments[3]
        
        # convert thrust percentage to pwm milliseconds
        for i in range(8):
            thrust_vals[i] /= 3 # we add 3 thrust percentages (all -100 to 100)
            print(f"0: {thrust_vals[0]}")
            #adjust for minimum thrust
            if -1*PIClient.MIN_THRUST_PERCENT < thrust_vals[i] and PIClient.MIN_THRUST_PERCENT > thrust_vals[i]:
                thrust_vals[i] = float(0)
            if PIClient.REVERSE_THRUSTS[i]:
                thrust_vals[i] = int(PIClient.CENTER_THRUST + -1 * thrust_vals[i] / 100.0 * PIClient.MAX_THRUST)
            else:
                thrust_vals[i] = int(PIClient.CENTER_THRUST + thrust_vals[i] / 100.0  * PIClient.MAX_THRUST)
            thrust_vals[i] = int(PIClient.CENTER_THRUST + thrust_vals[i] / 100.0 *  PIClient.MAX_THRUST)
        # if any thrusters somehow were above the threashold, get them under
        for i in range(8):
            if thrust_vals[i] > PIClient.MAX_THRUST:
                thrust_vals[i] = PIClient.MAX_THRUST
            if thrust_vals[i] < PIClient.MIN_THRUST:
                thrust_vals[i] = PIClient.MIN_THRUST
        send_bytes = bytearray(17)
        send_bytes[0:17] = struct.pack("=cHHHHHHHH", 0x01.to_bytes(length=1, byteorder='big', signed=False), thrust_vals[0], thrust_vals[1], thrust_vals[2], thrust_vals[3], thrust_vals[4], thrust_vals[5], thrust_vals[6], thrust_vals[7])
        print(f"sending data: {send_bytes}")
        self.out_queue.put(send_bytes)

    def set_manual_thrust(self, thrusts, verticle_thrust_adjustments=[0, 0, 0, 0]):
        assert isinstance(thrusts, list), "thrusts must be an array of floats"
        assert len(thrusts) == 6, "thrusts must be array of 6 floats"
        for i in range(len(thrusts)):
            try:
                thrusts[i] = float(thrusts[i])
            except ValueError:
                assert False, "data in thrusts must be float"
            assert thrusts[i] < 100 and thrusts[i] > -100, "data in thrusts must be float between -100 and 100"
        thrust_vals = [0, 0, 0, 0, 0, 0, 0, 0]  #thruster values in percentages (directly written), will be changed to milliseconds
        mov = PIClient.move(*thrusts)
        # forward / side thrusters
        thrust_vals[7] = mov.f - mov.s - mov.y
        thrust_vals[2] = mov.f + mov.s + mov.y
        thrust_vals[0] = mov.f - mov.s + mov.y
        thrust_vals[6] = mov.f + mov.s - mov.y
        # up thrusters
        thrust_vals[5] = mov.u + mov.p - mov.r + verticle_thrust_adjustments[0]
        thrust_vals[3] = mov.u + mov.p + mov.r + verticle_thrust_adjustments[1]
        thrust_vals[1] = mov.u - mov.p + mov.r + verticle_thrust_adjustments[2]
        thrust_vals[4] = mov.u - mov.p - mov.r + verticle_thrust_adjustments[3]
        
        # adjust all thrust values linearly down based on maximum thrust present
        thrust_percent = 1
        for i in range(8):
            if thrust_vals[i] != 0:
                curr_thrust_percent = abs(PIClient.MAX_THRUST_PERCENT/thrust_vals[i])
                if curr_thrust_percent < thrust_percent:
                    thrust_percent = curr_thrust_percent

        # convert thrust percentage to pwm milliseconds
        for i in range(8):
            #adjust for minimum thrust
            if -1*PIClient.MIN_THRUST_PERCENT < thrust_vals[i] and PIClient.MIN_THRUST_PERCENT > thrust_vals[i]:
                thrust_vals[i] = float(0)
            if PIClient.REVERSE_THRUSTS[i]:
                thrust_vals[i] = int(PIClient.CENTER_THRUST + -1 * thrust_vals[i] / 100.0 * thrust_percent * PIClient.MAX_THRUST)
            else:
                thrust_vals[i] = int(PIClient.CENTER_THRUST + thrust_vals[i] / 100.0 * thrust_percent * PIClient.MAX_THRUST)
        send_bytes = bytearray(17)
        send_bytes[0:17] = struct.pack("=cHHHHHHHH", 0x01.to_bytes(length=1, byteorder='big', signed=False), thrust_vals[0], thrust_vals[1], thrust_vals[2], thrust_vals[3], thrust_vals[4], thrust_vals[5], thrust_vals[6], thrust_vals[7])
        print(f"writing thrusters {thrust_vals}")
        self.out_queue.put(send_bytes)

    def move_claw(self, claw_num, claw_deg):
        assert isinstance(claw_num, int), "claw_num must be an int specifying the selected claw"
        assert isinstance(claw_deg, int), "claw_deg must be an int specifying the degree to write to the selected claw"
        # assert claw_deg <= 2000 and claw_deg >= 1000, "claw deg must be between 1000 and 2000"
        assert claw_num >= 0 and claw_num <= 1, "claw_num must be 0 or 1" 
        self.out_queue.put(struct.pack("=ccH", 0x02.to_bytes(length=1, byteorder='big', signed=False), claw_num.to_bytes(length=1, byteorder='big', signed=False), claw_deg))

    def turn_flashlight_off(self):
        self.out_queue.put(struct.pack("=cc", 0x03.to_bytes(length=1, byteorder='big', signed=False), 0x00.to_bytes(length=1, byteorder="big", signed=False)))

    def turn_flashlight_on(self):
        self.out_queue.put(struct.pack("=cc", 0x03.to_bytes(length=1, byteorder='big', signed=False), 0x01.to_bytes(length=1, byteorder="big", signed=False)))


if __name__ == "__main__":
    comms = PIClient(("192.168.13.100", 27777))
    while True:
        command = input()
        match(command):
            case 'tf':
                comms.set_manual_thrust([10.0, 0, 0, 0, 0, 0])
            case 'fs':
                comms.set_manual_thrust([0, 0, 0, 0, 0, 0])
            case 's1':
                comms.move_claw(0, int(input()))
            case 's0':
                comms.move_claw(1, int(input()))
            case 'on':
                comms.turn_flashlight_on()
            case 'off':
                comms.turn_flashlight_off()
