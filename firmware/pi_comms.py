# import RPi.GPIO as GPIO
import socket, select, queue

class PIComms:
    def __init__(self, address):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(address)
        self.sock.listen(0)
        self.sc, self.sockname = self.sock.accept()

        self.poller = select.poll()
        self.poller.register(self.sc)
        self.out_queue = queue.Queue()
        
        while True:
            events = self.poller.poll()
            for sock, event in events:
                if event == select.POLLIN:
                    in_data = sock.recv(2048)
                if event == select.POLLOUT and self.out_queue.not_empty():
                    sock.sendall(self.out_queue.get())
                if event == select.POLLPRI:
                    pass

if __name__ == "__main__":
    comms = PIComms(("0.0.0.0", 7772))