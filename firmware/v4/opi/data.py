# interperates and stores IMU data. Also autoreports data to surface.
from dataclasses import dataclass


@dataclass
class data:
    accel:list[float]
    gyro:list[float]
    angles:list[float]
    velocity:list[float]

class OpiDataProcess:
    def __init__(self):
        pass

    # turns acceleration into velocity
    def calc_velocity(self):
        pass

    def autoreport_data(self):
        pass