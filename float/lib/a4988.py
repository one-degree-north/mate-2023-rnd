import board
import digitalio
import time

class StepperDriver:
    def __init__(self, dir_pin, step_pin, delay=1e-6):
        self._init(dir_pin, step_pin)
        self.delay = delay
        self.dir_pin = dir_pin
        self.step_pin = step_pin

    def _init(self, dir_pin, step_pin):
        self._dir = digitalio.DigitalInOut(dir_pin)
        self._step = digitalio.DigitalInOut(step_pin)

        self._dir.direction = digitalio.Direction.OUTPUT
        self._step.direction = digitalio.Direction.OUTPUT

        self._dir.value = False
        self._step.value = False

    def _pulse(self):
        self._step.value = True
        time.sleep(self.delay)
        self._step.value = False
        time.sleep(self.delay)

    def step(self, forward=True):
        self._dir.value = forward
        self._pulse()

    def move(self, steps, step_delay_ms):
        self._dir.value = (steps >= 0)
        for i in range(abs(steps)):
            self._pulse()
            time.sleep(step_delay_ms / 1000.0)

    def deinit(self):
        self._dir.deinit()
        self._step.deinit()
        self._dir = None
        self._step = None

    def reinit(self):
        self._init(self.dir_pin, self.step_pin)

    def __enter__(self):
        return self

    def __exit__(self):
        self.deinit()

    def __repr__(self):
        return f"<stepper(dir={self.dir_pin},step={self.step_pin}),enabled={self._dir and self._step}>"
