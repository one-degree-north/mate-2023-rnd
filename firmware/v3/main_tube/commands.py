from utils import *
from mcu_interface.mcu_utils import *
from mcu_interface.mcu_constants import *
from mcu_interface.interface import *

def cmd_test(mcu: MCUInterface):
    mcu.send_packet(0x00, 0x00, 0x00, bytes([]))

def cmd_echo(mcu: MCUInterface, word: str):
    mcu.send_packet(0x00, 0x00, len(word), bytes(word))

def cmd_reset(mcu: MCUInterface):
    mcu.send_packet(0x01, 0x00, 0x00, bytes([]))

def cmd_continue(mcu: MCUInterface):
    mcu.send_packet(0x02, 0x00, 0x00, bytes([]))

def cmd_stop(mcu: MCUInterface):
    mcu.send_packet(0x03, 0x00, 0x00, bytes([]))

def cmd_get_attr(mcu: MCUInterface, param: int):
    mcu.send_packet(0x0A, param, 0x00, bytes([]))

def cmd_thruster(mcu: MCUInterface, thruster: int, value: int):
    assert 0 <= thruster <= 5 or THRUSTER_ONE <= thruster <= THRUSTER_SIX
    assert 1000 <= value <= 2000

    if thruster < THRUSTER_ONE:
        thruster += THRUSTER_ONE

    mcu.send_packet(0x18, thruster, 2, struct.pack('>H', value))
    
def cmd_horizontal_thrusters(mcu: MCUInterface, values: Union[tuple[int], list[int]]):
    assert len(values) == 2

    # check through each value just in case
    # left, right
    for i in range(0, 2, 1):
        assert 1000 <= val <= 2000
        mcu.send_packet(0x18, THRUSTER_ONE+i, 2, struct.pack('>H', values[i]))
    
def cmd_vertical_thrusters(mcu: MCUInterface, values: Union[tuple[int], list[int]]):
    assert len(values) == 4

    # check through each value just in case
    # front left, front right, back left, back right
    for i in range(0, 4, 1):
        assert 1000 <= values[i] <= 2000
        mcu.send_packet(0x18, THRUSTER_THREE+i, 2, struct.pack('>H', values[i]))

def cmd_all_thrusters(mcu: MCUInterface, values: Union[tuple[int], list[int]]):
    assert len(values) == 6

    # check through each value just in case
    for val in values:
        assert 1000 <= val <= 2000

    mcu.send_packet(0x18, THRUSTER_ALL, 12, struct.pack('>HHHHHH', *values))

def cmd_thruster_mask(mcu: MCUInterface, thrusters: Union[tuple[int], list[int]], value: int):
    mask = 0b11000000
    for val in thrusters:
        if val > 0x05:
            val -= THRUSTER_ONE
        assert 0 <= val <= 5
        mask |= (1 << val)

    mcu.send_packet(0x19, mask, 2, struct.pack('>H', value))

def cmd_servo(mcu: MCUInterface, servo: int, value: int):
    assert 0 <= servo <= 1 or SERVO_LEFT <= servo <= SERVO_RIGHT
    assert 1000 <= value <= 2000

    if servo < SERVO_LEFT:
        servo += SERVO_LEFT

    mcu.send_packet(0x28, servo, 2, struct.pack('>H', value))

def cmd_all_servos(mcu: MCUInterface, values: Union[Vector2, tuple[int], list[int]]):
    assert len(values) == 2

    assert 1000 <= values[0] <= 2000
    assert 1000 <= values[1] <= 2000

    mcu.send_packet(0x28, SERVO_ALL, 4, struct.pack('>HH', values[0], values[1]))

def cmd_get_thruster(mcu: MCUInterface, thruster: int):
    assert 0 <= thruster <= 5 or THRUSTER_ONE <= thruster <= THRUSTER_SIX

    if thruster < THRUSTER_ONE:
        thruster += THRUSTER_ONE

    mcu.send_packet(0x1A, thruster, 0, bytes([]))

def cmd_get_servo(mcu: MCUInterface, servo: int):
    assert 0 <= servo <= 1 or SERVO_LEFT <= servo <= SERVO_RIGHT

    if servo < SERVO_LEFT:
        servo += SERVO_LEFT

    mcu.send_packet(0x2A, servo, 0, bytes([]))

def cmd_get_sensor(mcu: MCUInterface, sensor: int):
    assert SENSOR_ACCEL <= sensor <= SENSOR_ALL

    mcu.send_packet(0x32, sensor, 0, bytes([]))

def cmd_set_auto_report_interval(mcu: MCUInterface, interval: float):
    # change into multiples of 100us
    interval_hus = int(interval * 10000) & 0xFFFF

    mcu.send_packet(0x35, SENSOR_ALL, 2, struct.pack('>H', interval_hus))

def cmd_set_auto_report(mcu: MCUInterface, sensor: int, enabled: bool):
    assert SENSOR_ACCEL <= sensor <= SENSOR_ALL

    mcu.send_packet(0x35, sensor, 1, bytes([1 if enabled else 0]))

def cmd_set_auto_report_mask(mcu: MCUInterface, sensors: Union[tuple[int], list[int]], enabled: int):
    mask = 0b0000000000000000
    for val in sensors:
        assert SENSOR_ACCEL <= sensor <= SENSOR_ALL
        mask_point = val - SENSOR_ACCEL
        mask |= (1 << mask_point)

    mcu.send_packet(0x35, SENSOR_ALL, 3, struct.pack('>BH', 1 if enabled else 0, mask))