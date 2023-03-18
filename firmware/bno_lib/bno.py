import subprocess
import dataclasses
import enum

# not sure why, enum has no attribute StrEnum for me
# class BNOPowerMode(enum.StrEnum):
#     NORMAL = auto()
#     LOW = auto()
#     SUSPEND = auto()


# class BNOOperationalMode(enum.StrEnum):
#     CONFIG = auto()
#     ACCONLY = auto()
#     MAGONLY = auto()
#     GYRONLY = auto()
#     ACCMAG = auto()
#     ACCGYRO = auto()
#     MAGGYRO = auto()
#     AMG = auto()
#     IMU = auto()
#     COMPASS = auto()
#     M4G = auto()
#     NDOF = auto()
#     NDOF_FMC = auto()


# class BNODataOutputType(enum.StrEnum):
#     ACC = auto()
#     GYR = auto()
#     MAG = auto()
#     EUL = auto()
#     QUA = auto()
#     GRA = auto()
#     LIN = auto()
#     INF = auto()
#     CAL = auto()
#     CON = auto()


class BNOPowerMode(enum.Enum):
    NORMAL = "normal"
    LOW = "low"
    SUSPEND = "suspend"


class BNOOperationalMode(enum.Enum):
    CONFIG = "config"
    ACCONLY = "acconly"
    MAGONLY = "magonly"
    GYRONLY = "gyronly"
    ACCMAG = "accmag"
    ACCGYRO = "accgyro"
    MAGGYRO = "maggyro"
    AMG = "amg"
    IMU = "imu"
    COMPASS = "compass"
    M4G = "m4g"
    NDOF = "ndof"
    NDOF_FMC = "ndof_fmc"


class BNODataOutputType(enum.Enum):
    ACC = "acc"
    GYR = "gyr"
    MAG = "mag"
    EUL = "eul"
    QUA = "qua"
    GRA = "gra"
    LIN = "lin"
    INF = "inf"
    CAL = "cal"
    CON = "con"

class BNOSensor:
    def __init__(self, bus='/dev/i2c-1', address=0x28):
        self.bus = bus
        self.address = address
        self.mode = BNOOperationalMode.NDOF_FMC
        self.power_mode = BNOPowerMode.NORMAL

        # reset the sensor
        c = self.reset()
        c = self.set_mode(self.mode)
        # check info too, just to make sure it's not broken'
        c = self.read(BNODataOutputType.INF)

    def reset(self) -> int:
        c = subprocess.run(["getbno055", "-a", hex(self.address), "-b", self.bus, "-r"], capture_output=True)
        if c.returncode or "error" in c.stdout.decode("utf-8").lower():
            raise RuntimeError(c.stdout)
        return c.returncode

    def read(self, data_type: BNODataOutputType) -> dict:
        # run the subprocess -t
        c = subprocess.run(["getbno055", "-a", hex(self.address), "-b", self.bus, "-t", data_type.value], capture_output=True)
        out_str = c.stdout.decode("utf-8")
        if c.returncode or "error" in out_str.lower() and data_type.value != "inf":
            raise RuntimeError(out_str)

        # process it TODO: WIP
        if data_type.value in ("acc", "gyr", "mag", "eul", "gra", "lin"):
            split = out_str.split(" ")
            typ = str(split[0])
            x = float(split[1])
            y = float(split[2])
            z = float(split[3])
            return {data_type: (x, y, z)}
        elif data_type.value == "qua":
            split = out_str.split(" ")
            typ = str(split[0])
            w = float(split[1])
            x = float(split[2])
            y = float(split[3])
            z = float(split[4])
            return {data_type: (w, x, y, z)}
        # TODO: finish the parsing
        elif data_type.value == "inf":
            return
        elif data_type.value == "cal":
            return
        elif data_type.value == "con":
            return

    def dump(self):
        c = subprocess.run(["getbno055", "-a", hex(self.address), "-b", self.bus, "-d"], capture_output=True)
        if c.returncode or "error" in c.stdout.decode("utf-8").lower():
            raise RuntimeError(c.stdout)
        return

    def set_mode(self, mode: BNOOperationalMode) -> BNOOperationalMode:
        c = subprocess.run(["getbno055", "-a", hex(self.address), "-b", self.bus, "-m", mode.value], capture_output=True)
        if c.returncode or "error" in c.stdout.decode("utf-8").lower():
            raise RuntimeError(c.stdout)
        self.mode = mode
        return self.mode

    def set_power_mode(self, mode: BNOPowerMode) -> BNOPowerMode:
        c = subprocess.run(["getbno055", "-a", hex(self.address), "-b", self.bus, "-p", mode.value], capture_output=True)
        if c.returncode or "error" in c.stdout.decode("utf-8").lower():
            raise RuntimeError(c.stdout)
        self.power_mode = mode
        return self.power_mode

    def load_calibration(self, absolute_path: str) -> dict:
        c = subprocess.run(["getbno055", "-a", hex(self.address), "-b", self.bus, "-l", absolute_path], capture_output=True)
        if c.returncode or "error" in c.stdout.decode("utf-8").lower():
            raise RuntimeError(c.stdout)

        # return calibrations loaded
        return self.read(BNODataOutputType.CAL)

    def write_calibration(self, absolute_path: str) -> str:
        c = subprocess.run(["getbno055", "-a", hex(self.address), "-b", self.bus, "-w", absolute_path], capture_output=True)
        if c.returncode or "error" in c.stdout.decode("utf-8").lower():
            raise RuntimeError(c.stdout)
        f = open(absolute_path, 'r')
        r = f.read()
        f.close()
        return r

    def output_to_html(self, data_type: BNODataOutputType, absolute_path: str) -> str:
        c = subprocess.run(["getbno055", "-a", hex(self.address), "-b", self.bus, "-t", data_type.value, "-o", absolute_path], capture_output=True)
        if c.returncode or "error" in c.stdout.decode("utf-8").lower():
            raise RuntimeError(c.stdout)
        f = open(absolute_path, 'r')
        r = f.read()
        f.close()
        return r

    def __repr__(self):
        return f"<BNOSensor[{self.bus}, {self.address}, {self.mode}, {self.power_mode}]>"


if __name__ == "__main__":
    bno = BNOSensor('/dev/i2c-3', 0x28)
    bno.set_mode(BNOOperationalMode.NDOF_FMC)
    print(bno.read(BNODataOutputType.EUL))
    print(bno.dump())
