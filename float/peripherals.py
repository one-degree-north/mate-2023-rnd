import busio
import board
import adafruit_bno055
import a4988


# initialize and create various drivers
# will block until they are properly initialized
# i2c: i2c bus, probably just board.I2C()
# returns tuple (BNO055_I2C, StepperDriver)
def get_peripherals(i2c):
    # bno055
    bno = None
    while not bno:
        try:
            bno = adafruit_bno055.BNO055_I2C(i2c)
        except OSError:
            pass

    # stepper driver
    step = a4988.StepperDriver(board.D39, board.D38)

    return (bno, step)
