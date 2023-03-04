THRUSTER_ONE = 0x00
THRUSTER_TWO = 0x01
THRUSTER_THREE = 0x02
THRUSTER_FOUR = 0x03
THRUSTER_FIVE = 0x04
THRUSTER_SIX = 0x05
THRUSTER_SEVEN = 0x06
THRUSTER_EIGHT = 0x07
THRUSTER_ALL = 0x1F

SENSOR_ACCEL = SENSOR_ACC = 0x30
SENSOR_MAG = SENSOR_MAGNET = 0x31
SENSOR_GYRO = SENSOR_GYR = 0x32
SENSOR_ORIENTATION = SENSOR_EULER = 0x33
SENSOR_QUATERNION = SENSOR_QUAT = 0x34
SENSOR_LINACCEL = SENSOR_LINEAR_ACCEL = 0x35
SENSOR_GRAVITY = 0x36
SENSOR_CALIBRATION = SENSOR_CALIB = 0x38
SENSOR_SYSTEM = 0x39
SENSOR_TEMP = SENSOR_TEMPERATURE = 0x3A
SENSOR_ALL = 0x3F

HEADER_RECV = 0xa7
HEADER_TRMT = 0x7a
FOOTER_RECV = 0xa7
FOOTER_TRMT = 0x7a

SUCCESS = 1
FAILURE = 0

PWM_MIN = 1000
PWM_MID = PWM_NEUTRAL = 1500
PWM_MAX = 2000
