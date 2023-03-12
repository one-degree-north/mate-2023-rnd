#server communicates with the surface
import threading, queue, socket, select

def OPiServer(self):
    def __init__(self, server_address: tuple, thruster_control):
        self.connected = False
        self.server_address = server_address
        self.thruster_control = thruster_control
        self.client_addr = ()
        self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
    
    # starts the server for surface client to communicate with
    def start_server(self, server_address: tuple):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(server_address)
        self.self_addr = server_address
        print(f"server set up at {server_address}")
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
        if cmd == 0x00: # hold
            pass
        elif cmd == 0x01: # move velocity
            pass
        elif cmd == 0x02: # move rotational velocity
            pass
        elif cmd == 0x03: # goto rotational angle
            pass
        elif cmd == 0x04: # drift
            pass
    
    def send_data(self, data):
        self.out_queue.put(data)
    
    def send_sens_data(self, param, values):
        pass