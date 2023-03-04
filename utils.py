# mcu_utils.py
# various utilities for the other scripts.

from typing import Union, List, Tuple

INVALID = 0x82D3F263


class Vector3:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, key):
        assert type(key) == int and 0 <= key <= 2
        return (self.x, self.y, self.z)[key]

    def __setitem__(self, key, newvalue):
        assert type(key) == int and 0 <= key <= 2
        assert type(newvalue) == float
        if key == 0:
            self.x = newvalue
        if key == 1:
            self.y = newvalue
        if key == 2:
            self.z = newvalue

    def __len__(self):
        return 3

    def set_axis(self, axis: int, value: float):
        if axis == 0:
            self.x = value
        elif axis == 1:
            self.y = value
        elif axis == 2:
            self.z = value
        else:
            raise IndexError("Invalid Axis")

    def get_axis(self, axis: int):
        if axis == 0:
            return self.x
        elif axis == 1:
            return self.y
        elif axis == 2:
            return self.z
        else:
            raise IndexError("Invalid Axis")

    def is_valid(self):
        return self.x != INVALID and self.y != INVALID and self.z != INVALID

    def __str__(self):
        return f"({self.x:.4f}, {self.y:.4f}, {self.z:.4f})"

    @staticmethod
    def new():
        return Vector3(0, 0, 0)

    @staticmethod
    def invalid():
        return Vector3(INVALID, INVALID, INVALID)

    @staticmethod
    def from_arr(i: Union[List, Tuple]):
        return Vector3(i[0], i[1], i[2])


class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __getitem__(self, key):
        assert type(key) == int and 0 <= key <= 1
        return (self.x, self.y, self.z)[key]

    def __setitem__(self, key, newvalue):
        assert type(key) == int and 0 <= key <= 1
        assert type(newvalue) == float
        if key == 0:
            self.x = newvalue
        if key == 1:
            self.y = newvalue

    def __len__(self):
        return 2

    @staticmethod
    def new():
        return Vector2(0, 0)


class Quaternion:
    def __init__(self, w: float, x: float, y: float, z: float):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, key):
        assert type(key) == int and 0 <= key <= 3
        return (self.w, self.x, self.y, self.z)[key]

    def __setitem__(self, key, newvalue):
        assert type(key) == int and 0 <= key <= 3
        assert type(newvalue) == float
        if key == 0:
            self.w = newvalue
        if key == 1:
            self.x = newvalue
        if key == 2:
            self.y = newvalue
        if key == 3:
            self.z = newvalue

    def __len__(self):
        return 4

    @staticmethod
    def new():
        return Quaternion(0, 0, 0, 0)

    @staticmethod
    def from_arr(i: Union[List, Tuple]):
        return Quaternion(i[0], i[1], i[2], i[3])