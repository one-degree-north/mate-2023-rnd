from dataclasses import dataclass
import sys
from pathlib import Path
path = Path(sys.path[0])
sys.path.insert(1, str((path.parent).absolute()))
# sys.path.insert(1, str((path.parent.parent.parent.).absolute()))
print(sys.path)

from utils import *
from firmware.v3.main_tube.mcu_constants import *


@dataclass
class BNOStatus:
    calib_sys: int
    calib_gyr: int
    calib_acc: int
    calib_mag: int
    sys_status: int
    sys_err: int

    def __init__(self):
        self.calib_sys = self.calib_mag = self.calib_gyr = self.calib_acc = 0
        self.sys_status = 0
        self.sys_err = 0


@dataclass
class SystemStatus:
    sys_enable: int
    failed: int

    def __init__(self):
        self.sys_enable = 1
        self.failed = 0


@dataclass
class PWMValue:
    # intended to store values of microsecond PWM
    # 1000-2000
    value: int


@dataclass
class ThrusterServoData:
    thrusters: tuple[PWMValue]
    servos: tuple[PWMValue]

    def __init__(self):
        self.thrusters = tuple([PWMValue(1500) for i in range(6)])
        self.servos = tuple([PWMValue(1500) for i in range(2)])

    def update(self, param: int, value: int):
        if THRUSTER_ONE <= param <= THRUSTER_SIX:
            self.thrusters[param - THRUSTER_ONE].value = value
        # if SERVO_LEFT <= param <= SERVO_RIGHT:
        #     self.servos[param - SERVO_LEFT].value = value

    def update_all_thrusters(self, values):
        for i in range(6):
            self.thrusters[i].value = values[i]

    def update_all_servos(self, values):
        for i in range(2):
            self.servos[i].value = values[i]


@dataclass
class SensorData:
    accel: Vector3
    mag: Vector3
    gyro: Vector3
    orientation: Vector3
    quaternion: Quaternion
    linaccel: Vector3
    gravity: Vector3
    status: BNOStatus
    system: SystemStatus
    outputs: ThrusterServoData
    temperature: float
    voltage: float
    depth: float
    killswitch: bool
    other: str

    def __init__(self):
        self.accel = Vector3.new()
        self.mag = Vector3.new()
        self.gyro = Vector3.new()
        self.orientation = Vector3.new()
        self.quaternion = Quaternion.new()
        self.linaccel = Vector3.new()
        self.gravity = Vector3.new()
        self.status = BNOStatus()
        self.system = SystemStatus()
        self.outputs = ThrusterServoData()
        self.temperature = 0.0
        self.voltage = 12  # hopefully!
        self.depth = 0
        self.killswitch = False
        self.other = ''

def depth_mapping(value: int) -> float:
    volts = value / 0xFFFF * 3.3
    kPa = (volts - 0.5) * 400 + 100
    meters = (kPa - 100) / 9.78
    return meters


SENSOR_TYPES = {
        SENSOR_ACCEL: Vector3,
        SENSOR_MAG: Vector3,
        SENSOR_GYRO: Vector3,
        SENSOR_EULER: Vector3,
        SENSOR_QUAT: Quaternion,
        SENSOR_LINACCEL: Vector3,
        SENSOR_GRAVITY: Vector3,
        SENSOR_CALIB: int,
        SENSOR_SYSTEM: int,
        SENSOR_TEMP: int,
}