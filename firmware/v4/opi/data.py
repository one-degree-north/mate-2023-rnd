# interperates and stores IMU data. Also autoreports data to surface.
from dataclasses import dataclass
from queue import Queue
from threading import Thread
import time

import sys
from pathlib import Path
path = Path(sys.path[0])
sys.path.insert(1, str((path.parent.parent).absolute()))

from bno_lib.bno import *


@dataclass
class OpiDataBlock:
    accel:  list[float]
    gyro:   list[float]
    eul:    list[float]
    vel:    list[float]
    quat:   list[float]
    lin:    list[float]
    inf:    list[float]    # information
    cal:    list[float]    # calibration
    con:    list[float]    # continuous data (?), CHANGE THIS!!
    mag:    list[float]
    gra:    list[float]    # gravitational vector

    def __init__(self):
        self.accel = [0, 0, 0]
        self.gyro = [0, 0, 0]
        self.eul = [0, 0, 0]
        self.vel = [0, 0, 0]
        self.quat = [0, 0, 0, 0]
        self.lin = [0, 0, 0]
        self.inf = [0, 0, 0]    # not sure how this should be represented
        self.cal = [0, 0, 0]    # also not sure
        self.con = [0, 0, 0]
        self.mag = [0, 0, 0]
        self.gra = [0, 0, 0]

    # I don't want to use a dict, ok?
    def set_value(self, key, value):
        if key == BNODataOutputType.ACC:
            self.accel = value
        elif key ==  BNODataOutputType.GYR:
            self.gyro = value
        elif key ==  BNODataOutputType.EUL:
            self.eul = value
        elif key ==  BNODataOutputType.MAG:
            self.mag = value
        elif key ==  BNODataOutputType.QUA:
            self.quat = value
        elif key ==  BNODataOutputType.GRA:
            self.gra = value
        elif key ==  BNODataOutputType.LIN:
            self.lin = value
        elif key ==  BNODataOutputType.INF:
            self.inf = value
        elif key ==  BNODataOutputType.CAL:
            self.cal = value
        elif key ==  BNODataOutputType.CON:
            self.con = value
    
    # not sure if this is the best method, whatever though
    def update_vel(self, delta_time, accel):
        for i in range(3):
            self.vel[i] += accel[i] * delta_time  # delta time is in seconds


class OpiDataProcess:
    def __init__(self, report_data=True, stop_event=None):
        self.server = None
        self.bno_sensor = BNOSensor()

        self.bno_read_delay = 0.01    # in seconds
        self.bno_individual_delay = self.bno_read_delay / 9.0
        self.bno_fetch_delay = self.bno_read_delay / 2.0
        self.bno_queue = Queue()

        self.data = OpiDataBlock()

        self.bno_read_thread = Thread(target=self.bno_read_loop, args=(self.bno_queue,))
        self.bno_fetch_thread = Thread(target=self.bno_fetch_loop, args=(self.bno_queue,))
        self.report_data = report_data   # report data to surface
        self.stop_event=stop_event

    def set_server(self, server):
        self.server = server

    def start_bno_reading(self):
        self.bno_fetch_thread.start()
        self.bno_read_thread.start()

    # read all bno data
    def read_bno_data(self, q):
        for bno_data in BNODataOutputType:
            if bno_data == BNODataOutputType.CON:
                continue

            # read the data value from the sensor
            bno_return = {bno_data: (2, 2, 2)}# self.bno_sensor.read(bno_data)

            if bno_return != None:
                q.put((bno_data, bno_return))

            time.sleep(self.bno_individual_delay)

    # using a thread to continuously get BNO data
    def bno_read_loop(self, q):
        while not self.stop_event.is_set():
            self.read_bno_data(q)
            time.sleep(self.bno_read_delay)
            # print(f"sleeping {self.bno_read_delay}")

    def bno_fetch_loop(self, q):
        while not self.stop_event.is_set():
            while not q.empty():
                component, value = q.get()
                self.data.set_value(component, value[component])
            self.data.update_vel(self.bno_read_delay, self.data.lin)
            time.sleep(self.bno_fetch_delay)

    def set_read_delay(self, read_delay):
        self.bno_read_delay = read_delay

    # turns acceleration into velocity
    def calc_velocity(self):
        pass

    # change autoreport time
    def autoreport_data(self):
        pass


if __name__ == "__main__":
    opi_data = OpiDataProcess(report_data=False)
    opi_data.start_bno_reading()
    while True:
        time.sleep(0.1)
        print(opi_data.data.accel)
        print(opi_data.data.eul)
        print(opi_data.data.lin)
        print(opi_data.data.vel)
