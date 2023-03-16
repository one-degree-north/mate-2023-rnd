# Controls thruster movement
from abc import ABC, abstractmethod, abstractproperty
import time, named
from collections import namedtuple

move = namedtuple("move", ['f', 's', 'u', 'p', 'r', 'y'])

class OpiPosState(ABC):
    @abstractmethod
    def on_tick(): # returns thruster outputs for a single tick
        pass
    @abstractproperty
    def move_type():
        return "def"
    @abstractmethod
    def set_target():
        pass

# move with thruster values (-1 to 1)
class OpiMoveRawState(OpiPosState):
    def __init__(self, movements, opi_data):
        self.movements = movements
        self.opi_data = opi_data

    def on_tick(self):
        pass

    def set_target(self, movements):
        self.target_vel = target_vel

    def move_type(self):
        return "move"

class OpiManualMoveState(OpiPosState):
    def __init__(self, manual, opi_data):
        self.manual = manual
        self.data = opi_data
    
    def on_tick(self):
        self.manual = 0
        for i in range(3):
            if abs(self.target_vel[i]) > self.manual:
                self.manual = abs(self.target_vel[i])
        adjust_vel = [0, 0, 0]
        for i in range(3):
            adjust_vel[i] = self.target_vel[i]/self.manual
        for i in range(3):
            if adjust_vel[i] > 1:
                adjust_vel[i] = 1
            if adjust_vel[i] < -1:
                adjust_vel[i] = -1
        return adjust_vel

    def set_target(self, manual):
        self.manual = manual

    def move_type(self):
        return "manual"

class OpiPosPidMoveState(OpiPosState):
    def __init__(self, target_vel, opi_data):
        self.target_vel = target_vel
        self.data = opi_data

    def on_tick(self):
        pass

    def set_target(self, target_vel):
        self.target_vel = target_vel

    def move_type(self):
        return "pid"

class OpiPosHoldState(OpiPosState):
    def __init__(self, opi_data):
        self.data = opi_data

    def on_tick(self, target_vel, opi_data):
        return [0, 0, 0]    # placeholder right now!

    def move_type(self):
        return "hold"

class OpiPosDriftState(OpiPosState):
    def on_tick(self, target_vel, opi_data):
        return [0, 0, 0]
    
    def move_type(self):
        return "drift"

class OpiRotateState(ABC):
    @abstractmethod
    def on_tick(): # returns thruster outputs for a single tick
        pass

class OpiRotManualState(OpiRotateState):
    pass

class OpiAngleMoveState(OpiRotateState):
    pass

class OpiRotHoldState(OpiRotateState):
    pass

class OpiRotDriftState(OpiRotateState):
    def on_tick():
        pass

class ThrusterController:
    def __init__(self, move_delta_time=0.05):
        self.data = None
        self.pos_state = OpiPosMoveState()
        self.rotate_state = OpiRotDriftState()
        self.move_delta_time = move_delta_time
        self.mcu_interface = None
    
    # way to solve circular dependency
    def set_interface(self, mcu_interface):
        self.mcu_interface = mcu_interface

    def set_data(self, opi_data):
        self.data = opi_data

    # moves ROV based on input data
    def move_loop(self):
        while True:
            pos_thrust = self.pos_state.on_tick(self.move_delta_time)
            rot_thrust = self.rotate_state.on_tick(self.move_delta_time)
            # somehow integrate pos_thrust and rot_thrust
            # transform forward, side, up, pitch, roll, yaw to thruster speeds
            mov = move(0, 0, 0, 0, 0, 0) # simplified thrusters with f, s, u, p, r, y
            for i in range(3):
                mov[i] = pos_thrust[i]
                mov[i+3] = rot_thrust[i]
            total_thrust = [0, 0, 0, 0, 0, 0, 0, 0]
            total_thrust[0] = mov.f - mov.s - mov.y
            total_thrust[1] = mov.f + mov.s + mov.y
            total_thrust[2] = mov.f - mov.s + mov.y
            total_thrust[3] = mov.f + mov.s - mov.y

            total_thrust[4] = mov.u + mov.p - mov.r
            total_thrust[5] = mov.u + mov.p + mov.r
            total_thrust[6] = mov.u - mov.p + mov.r
            total_thrust[7] = mov.u - mov.p - mov.r

            # get maximum thrust
            max_thrust = 0
            for i in range(8):
                total_thrust[i] = pos_thrust[i] + rot_thrust[i]
                if abs(total_thrust[i]) > max_thrust:
                    max_thrust = abs(total_thrust[i])
            # adjust all thrusts for maximum
            if max_thrust > 1:
                for i in range(8):
                    total_thrust[i] = int(total_thrust[i] / max_thrust)
                    # adjust for microseconds (-1 to 1) to (1000 to 2000)
                    total_thrust[i] = 1500 + 500*total_thrust[i]
                    # last adjustment in case total_thrust[i] was above 2000 or below 1000
                    if total_thrust[i] < 1000:
                        total_thrust[i] = 1000
                    if total_thrust[i] > 2000:
                        total_thrust[i] = 2000
            # move with all thrusts
            self.mcu_interface.set_thruster()
            time.sleep(self.move_delta_time)
    #set target velocity
    def move_vel():
        pass

    # set target rotational velocity
    def move_rot_vel():
        pass
    
    #set target rotational angle
    def set_angle():
        pass
    
    def set_hold():
        pass
    
    #no PID allowed here
    def set_drift():
        pass
"""
BBBB   III  GGGG
B   B   I  G
BBBB    I  G  GG
B   B   I  G   G
BBBB   III  GGGG

 CCCC H   H U   U N   N  GGGG U   U  SSSS
C     H   H U   U NN  N G     U   U S
C     HHHHH U   U N N N G  GG U   U  SSS
C     H   H U   U N  NN G   G U   U     S
 CCCC H   H  UUU  N   N  GGGG  UUU  SSSS
"""