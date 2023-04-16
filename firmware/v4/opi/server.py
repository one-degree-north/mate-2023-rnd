#server communicates with the surface
import threading, queue, socket, select, struct

"""
BBBB   III  GGGG
B   B   I  G
BBBB    I  G  GG
B   B   I  G   G
BBBB   III  GGGG

 CCCC H   H U   U N   N  GGGG U   U  SSSS
C     H   H U   U NN  N G     U   U S
C     HHHHH U   U N N N G  GG U   U  SSS
C     H   H U   U N  NN G   G U   U     S
 CCCC H   H  UUU  N   N  GGGG  UUU  SSSS
"""

class OPiServer:
    def __init__(self, server_address: tuple):
        self.connected = False
        self.server_address = server_address
        self.thruster_control = None
        self.interface = None
        self.client_addr = ()
        self.server_thread = threading.Thread(target=self._server_loop)
        self.out_queue = queue.Queue()
    
    def set_thruster_control(self, thruster_control):
        self.thruster_control = thruster_control

    def set_interface(self, interface):
        self.interface = interface

    # starts the server for surface client to communicate with
    def start_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_address)
        self.self_addr = self.server_address
        print(f"server set up at {self.server_address}")
        self.server_thread.start()

    # read and write data to and from surface client
    def _server_loop(self):
        while True:
            r, w, x = select.select([self.sock], [self.sock], [self.sock])
            for sock in r:  #ready to read!
                print("attempting to read network data")
                data, address = sock.recvfrom(2048)
                if address != self.client_addr: #client switched address (something wrong happened)
                    self.client_addr = address
                self._parse_data(data)
            
            for sock in w:  #ready to write!
                if not self.out_queue.empty() and self.connected:
                    print(f"attempting to write to {self.client_addr}")
                    sock.sendto(self.out_queue.get(), self.client_addr)
            
            for sock in x:  #exception 8^(. Create new socket and try to connect again.
                print("exception apparently occured")
    
    #parse data from surface client
    def _parse_data(self, data):
        cmd = data[0]
        if cmd == 0x00: # manual move
            thrusts = struct.unpack("!fff", data[1:])
            print(f"manually moving with {thrusts}")
            self.thruster_control.set_pos_manual(list(thrusts))
        elif cmd == 0x01: # move velocity
            velocities = struct.unpack("!fff", data[1:])
            self.thruster_control.set_pos_target_vel(list(velocities))
        elif cmd == 0x02: # hold
            self.thruster_control.set_pos_hold()
        elif cmd == 0x03:   # pos drift
            self.thruster_control.set_pos_drift()
        elif cmd == 0x04:
            thrusts = struct.unpack("!fff", data[1:])
            self.thruster_control.set_rot_manual(list(thrusts))
        elif cmd == 0x05: # move rotational velocity
            velocities = struct.unpack("!fff", data[1:])
            self.thruster_control.set_rot_vel(list(velocities))
        elif cmd == 0x06: # goto rotational angle
            angle = struct.unpack("!fff", data[1:])
            self.thruster_control.set_rot_angle(list(angle))
        elif cmd == 0x07: # drift
            self.thruster_control.set_rot_drift()
        elif cmd == 0x08:
            self.thruster_control.set_rot_hold()
        elif cmd == 0x10:   # test conneciton
            self.interface.test_connection()
        elif cmd == 0x11:   # get thruster positions
            self.interface.get_thrusters()
        elif cmd == 0x20:   # move claw
            pass
        elif cmd == 0x30:   # turn flashlight on / off
            pass
    
    #data is little endian
    def send_data(self, data):
        self.out_queue.put(data)
    
    def send_confirmation(self):
        self.out_queue.put(struct.pack("Q"))

    def send_thruster_positions(self):
        pass

    def send_servo_positions(self):
        pass

    def send_flashlight(self):
        pass

    def send_sens_data(self, param, values):
        self.out_queue.put(struct.pack("!" + "B"*(3+len(values)), 0x33, param, len(values), *values))

if __name__ == "__main__":
    pass