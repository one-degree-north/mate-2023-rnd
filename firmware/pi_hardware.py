# pi_hardware.py
# classes and constants for pi hardware configuration

from time import sleep
from subprocess import Popen, PIPE, DEVNULL, STDOUT
from threading import Thread
from queue import Queue

class Flag:
    def __init__(self, flag):
        self.flag = flag

class Thrusters:
    def __init__(self, exec_name: str):
        self.subprocess = Popen([exec_name], stdout=DEVNULL, stdin=PIPE, stderr=STDOUT)
        self.flag = Flag(False)
        self.write_queue = Queue()
        self.thread = Thread(target=self._write_thrusters);

    def start(self):
        self.flag.flag = True
        self.thread.start()

    def _write_thrusters(self):
        while self.flag.flag:
            try:
                write = self.write_queue.get_nowait()
                print(write)
                print(self.subprocess.communicate(input=f"{write[0]}\n{write[1]}\n".encode()))
            except:
                pass
            #sleep(0.001)

    def stop(self):
        self.flag.flag = False
        self.thread.join()

    def write_thruster(self, number: int, us: int):
        assert 0 <= number <= 7 or number == 108
        assert 1000 <= us <= 1800
        self.write_queue.put((number, us))


if __name__ == "__main__":
    th = Thrusters("/home/user/mate-2023-rnd/firmware/thr_ctrl")
    th.start()

    while True:
        cmd = input().split(" ")
        print(cmd)

        num = int(cmd[0])
        us = int(cmd[1])

        if num == -1:
            th.stop()
            break

        th.write_thruster(num, us)

