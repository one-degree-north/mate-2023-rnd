import socket, queue, threading, select, asyncio, struct, cv2
from time import sleep

class UnityCommProtocol:
    def __init__(self, unity_comms):
        # self.update_vr_addr = update_vr_addr
        self.unity_comms = unity_comms

    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        if not self.unity_comms.connected_event.is_set():
            print("now connected")
            self.unity_comms.connected_event.set()
            self.unity_comms.connected = True
            self.unity_comms.vr_addr = addr
            self.transport.sendto((0x01).to_bytes(1, byteorder="big"), self.unity_comms.vr_addr)
        self.unity_comms.out_queue.put(data)
        # print(len(data))
        # print("data received: " + str(data))
        # print((data.hex()).upper())
        self.unity_comms.decipher_input(data)

    def error_received(self, exc):
        print("error: " + str(exc))
        self.unity_comms.connected_event.clear()
        self.unity_comms.connected = False

    def connection_lost(self, exc):
        print("connection lost, closed connection")
        self.unity_comms.connected_event.clear()
        self.unity_comms.connected = False
    

class UnityComms:
    def __init__(self, in_queue, out_queue, on_rotation=[], on_position=[]):  # on_rotation, on_position..., arrays of functions to be called when the values change
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
        
        # headset data!
        self.hset_rotation = [0, 0, 0]
        self.hset_position = [0, 0, 0]

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
            print(data.hex().upper())
            # print("trying to write")
            self.transport.sendto(data, self.vr_addr)
            return True
        else:
            return False

    def update_image(self, image=None, rotation=None): # update image by updating viewImage if image is None
        # print("udating image")
        if rotation == None:
            rotation = self.hset_rotation
        if image == None:
            print(rotation)
            self.write(struct.pack("=cfff", (0x02).to_bytes(1, byteorder="big"), rotation[0], rotation[1], rotation[2]))

    def read(self): # probably can make a better version of this
        while True:
            if not self.out_queue.empty:
                input_bytes = bytearray(self.out_queue.get())
                self.decipher_input(input_bytes)
        # print(out_queue.qsize())
        # read_future = asyncio.run_coroutine_threadsafe(out_queue.get(), self.loop)
        # while not read_future.done():
        #     print(read_future.done())
        # return read_future.result()

    def decipher_input(self, input_bytes):
        match input_bytes[0]:
            case 0x01: #ask to establish connection
                self.write((0x01).to_bytes(1, byteorder="big"))
            case 0x02:  # headset position
                # print("position: " + str(struct.unpack("=cfff", input_bytes)))
                self.hset_position = struct.unpack("=fff", input_bytes[1:])
            case 0x03:  # headset rotation
                # print("rotation: " + str(struct.unpack("=cfff", input_bytes)))
                self.hset_rotation = struct.unpack("=fff", input_bytes[1:])
            case 0x04:
                print("rotation (quat): ")

    def read_thread(self):
        while True:
            data = input("> ")
            if data == "read":
                receive = vr_comms.read()
                print(receive)
            else:
            # asyncio.run_coroutine_threadsafe(in_queue.put(data.encode("ascii")), vr_comms.loop)
                vr_comms.write(data.encode("ascii"))

def test_camera(unity_comms):
    print("AAAAAA")
    # vid = cv2.VideoCapture(0)
    im = cv2.imread(r'C:\Users\gold_\Downloads\Python-logo-notext.png')
    while True:
        # ret, frame = vid.read()
        sleep(0.01)
        # cv2.imwrite(r'C:\Users\sd6tu\Documents\mate-2023-rnd\vr\unity-vr\Assets\Resources\viewImage.png', im)
        unity_comms.update_image()

if __name__ == "__main__":
    in_queue = asyncio.Queue()
    # out_queue = asyncio.Queue()
    out_queue = queue.Queue()
    vr_comms = UnityComms(in_queue=in_queue, out_queue=out_queue)
    vid_thread = threading.Thread(target=test_camera, args=[vr_comms], daemon=True)
    # a_thread = threading.Thread(target=vr_comms.read_thread, args=[in_queue, vr_comms], daemon=True)
    # a_thread.start()
    vid_thread.start()
    vr_comms.start_connection()
    # vid_thread.start()