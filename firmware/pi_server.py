# import RPi.GPIO as GPIO
import socket, select, queue, struct

class PIServer:
    MAX_THRUST_PERCENT = 70 # max in thrust percent
    MIN_THRUST_PERCENT = 5 #mininum thrust, if lower, automatically go to minimum
    CENTER_THRUST = 1400    # center in milliseconds
    MAX_RANGE = 400 # maximum difference in milliseconds
    MAX_THRUST = CENTER_THRUST + MAX_RANGE * MAX_THRUST_PERCENT / 100.0
    MIN_THRUST = CENTER_THRUST - MAX_RANGE * MAX_THRUST_PERCENT / 100.0
    #code for opi server
    def __init__(self, server_address):
        self.connected = False
        self.out_queue = queue.Queue()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(server_address)
        print(f"server set up at {server_address}")
        self.client_addr = ()
        self.server_loop()

    def server_loop(self):
        while True: # server should only have 1 client
            r, w, x = select.select([self.sock], [self.sock], [self.sock])
            for sock in r:  #ready to read!
                data, address = sock.recvfrom(2048)
                self.process_data(data, address)
                print("received data")
            
            for sock in w:  #ready to write!
                if not self.out_queue.empty() and self.connected:
                    sock.sendto(self.out_queue.get(), self.client_addr)
                    print("wrote data")
            
            for sock in x:  #exception 8^(. Create new socket and try to connect again.
                break
            # events = self.poller.poll()
            # for sock, event in events:
            #     if event & select.POLLIN:   # can write data!
            #         data, address = sock.recvfrom(2048)
            #         print("server received data to process")
            #         self.process_data(data, address)
            #     if event & (select.POLLOUT | select.POLLPRI) and not self.out_queue.empty() and self.connected:    # can read data!
            #         sock.sendto(self.out_queue.get())  # WE SHOULDN'T BE SENDING DATA RIGHT NOW!
            #         print("server sent data?")
            #     if event & (select.POLLHUP | select.POLLERR): # problem with communications, disconnect client and try to find new one
            #         # not sure when this would happend with udp...
            #         self.connected = False
            #         print("server ERROR, disconnected")
            #         break
    
    def process_data(self, data, address):
        self.connected = True
        self.client_addr = address
        command = data[0]
        print(f"received data from {address} with command: {command}, datalen: {len(data)}")
        match (command):
            case 0x01:  #move thrusters
                thrust_vals = [PIServer.CENTER_THRUST, PIServer.CENTER_THRUST, PIServer.CENTER_THRUST, PIServer.CENTER_THRUST, PIServer.CENTER_THRUST, PIServer.CENTER_THRUST, PIServer.CENTER_THRUST, PIServer.CENTER_THRUST]
                if len(data) == 17:
                    thrust_vals[0], thrust_vals[1], thrust_vals[2], thrust_vals[3], thrust_vals[4], thrust_vals[5], thrust_vals[6], thrust_vals[7] = struct.unpack("=HHHHHHHH", data[1:17])
                    # if any thrusters somehow were above the threashold, get them under
                    print(f"data: {data}")
                    for i in range(8):
                        if thrust_vals[i] > PIServer.MAX_THRUST:
                            thrust_vals[i] = PIServer.MAX_THRUST
                        if thrust_vals[i] < PIServer.MIN_THRUST:
                            thrust_vals[i] = PIServer.MIN_THRUST
                    #DO PWM WITH THE THRUST_VALS
                    print(f"WRITING THRUST: {thrust_vals}")
            case 0x02:  #move servos
                if len(data) == 4:
                    claw_num, deg = struct.unpack("=cH", data[1:4])
                    #SEND SERIAL TO CLAW
                    print(f"moving servo, num: {claw_num}, deg: {deg}")
            case 0x03:  #toggle flashlight
                if len(data) == 2:
                    flash_on_off = data[1]
                    if flash_on_off == 0:
                        #TURN FLASHLIGHT OFF
                        print("flashlight off")
                        pass
                    else:
                        #TURN FLASHLIGHT ON
                        print("flashlight on")
                        pass


if __name__ == "__main__":
    comms = PIServer(("127.0.0.1", 7772))