# interperates and stores IMU data. Also autoreports data to surface.
from dataclasses import dataclass
import threading, time

@dataclass
class data:
    accel:list[float]
    gyro:list[float]
    angles:list[float]
    vel:list[float]
    quaternion:list[float]
    lin:list[float]
    inf:list[float]
    cal:list[float]
    con:list[float]
    mag:list[float]
    gra: list[float]
    # I don't want to use a dict, ok?
    def set_value(self, key, value):
        if key == "acc":
            self.accel = value
        elif key == "gyr":
            self.gyro = value
        elif key == "mag":
            self.mag = value
        elif key == "qua":
            self.quaternion = value
        elif key == "gra":
            self.gra = value # wtf does gra mean
        elif key == "lin":
            self.lin = value
        elif key == "inf":
            self.inf = value
        elif key == "cal":
            self.cal = value
        elif key == "con":
            self.con = value
    
    # not sure if this is the best method, whatever though
    def update_vel(self, delta_time, accel):
        self.vel += accel * delta_time  #delta time is in seconds

class OpiDataProcess:
    def __init__(self, report_data=True):
        self.server = None
        self.bno_sensor = BNOSensor()
        self.bno_read_delay = 0.01    # in seconds
        self.data = data()
        self.bno_thread = threading.Thread(target=self.bno_loop, daemon=True)
        self.report_data = report_data   # report data to surface

    def set_server(self, server):
        self.server = server

    def start_bno_reading(self):
        self.bno_thread.start()

    # read all bno data
    def read_bno_data(self):
        for bno_data in BNODataOutputType:
            bno_return = self.bno_sensor.read(bno_data)
            self.data.set_value(list(bno_return.keys())[0], list(bno_return.values())[0])
        self.data.update_vel(self.bno_read_delay, self.data.accel)

    # using a thread to continuously get BNO data
    def bno_loop(self):
        while True:
            self.read_bno_data()
            time.sleep(self.bno_read_delay)

    #only getting BNO data when needed
    def set_read_delay(self, read_delay):
        pass

    # turns acceleration into velocity
    def calc_velocity(self):
        pass

    # change autoreport time
    def autoreport_data(self):
        pass