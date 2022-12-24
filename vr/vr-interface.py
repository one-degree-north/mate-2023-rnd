import socket, queue, threading, select, asyncio, struct

class UnityCommProtocol:
    def __init__(self, unity_comms):
        # self.update_vr_addr = update_vr_addr
        self.unity_comms = unity_comms

    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        print("data received")
        if not self.unity_comms.connected_event.is_set():
            print("now connected")
            self.unity_comms.connected_event.set()
            self.unity_comms.connected = True
            self.unity_comms.vr_addr = addr
            self.transport.sendto("why".encode("ascii"), self.unity_comms.vr_addr)
        self.unity_comms.out_queue.put(data)
        print("data received: " + str(data))

    def error_received(self, exc):
        print("error: " + str(exc))
        self.unity_comms.connected_event.clear()
        self.unity_comms.connected = False

    def connection_lost(self, exc):
        print("connection lost, closed connection")
        self.unity_comms.connected_event.clear()
        self.unity_comms.connected = False
    

class UnityComms:
    def __init__(self, in_queue, out_queue):
        self.addr = ("127.0.0.1", 8008)
        self.connected_event = asyncio.Event()
        self.connected = False
        self.quit_reading = asyncio.Event()
        self.vr_addr = ()
        # self.out_queue = asyncio.Queue()  # not compatable with asyncio!
        # self.in_queue = asyncio.Queue()
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.addr)
        self.transport = None

    def start_connection(self):
        asyncio.run(self.create_connection())

    async def create_connection(self):
        self.loop = asyncio.get_running_loop()
        print("creating connection")
        self.transport, protocol = await self.loop.create_datagram_endpoint(lambda: UnityCommProtocol(self), sock=self.sock)
        await self.quit_reading.wait()
        # while True: #read looop
        #     await self.connected_event.wait()
        #     data = await self.in_queue.get()
        #     # print(self.in_queue.qsize())
        #     # add a disconnect command
        #     transport.sendto(data, self.vr_addr)

    def write(self, data):  # returns true if connected and written, false if not connected
        # asyncio.run_coroutine_threadsafe(in_queue.put(data), self.loop)
        if self.connected:
            print("trying to write")
            self.transport.sendto(data, self.vr_addr)
            return True
        else:
            return False

    def read(self): # probably can make a better version of this
        input_bytes = bytearray(self.out_queue.get())
        self.decipher_input(input_bytes)
        # print(out_queue.qsize())
        # read_future = asyncio.run_coroutine_threadsafe(out_queue.get(), self.loop)
        # while not read_future.done():
        #     print(read_future.done())
        # return read_future.result()

    def decipher_input(self, input_bytes):
        match input_bytes[0]:
            case 0x1b:  # headset thing
                pass
            case 0x3a:  # headset rotation
                print(input_bytes[1:])

def read_thread(in_queue, vr_comms):
    while True:
        data = input("> ")
        if data == "read":
            receive = vr_comms.read()
            print(receive)
        else:
        # asyncio.run_coroutine_threadsafe(in_queue.put(data.encode("ascii")), vr_comms.loop)
            vr_comms.write(data.encode("ascii"))


in_queue = asyncio.Queue()
# out_queue = asyncio.Queue()
out_queue = queue.Queue()

vr_comms = UnityComms(in_queue=in_queue, out_queue=out_queue)
a_thread = threading.Thread(target=read_thread, args=[in_queue, vr_comms], daemon=True)
a_thread.start()
vr_comms.start_connection()