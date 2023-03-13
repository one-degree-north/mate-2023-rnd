# Controls thruster movement
from abc import ABC, abstractmethod, abstractproperty
import time

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

class OpiPosMoveState(OpiPosState):
    def __init__(self, target_vel, opi_data):
        self.target_vel = target_vel
        self.opi_data = opi_data

    def on_tick(self):
        # pretty dumb right now, turn into unit vector and send
        max_vel = 0
        for i in range(3):
            if abs(self.target_vel[i]) > max_vel:
                max_vel = abs(self.target_vel[i])
        adjust_vel = [0, 0, 0]
        for i in range(3):
            adjust_vel[i] = self.target_vel[i]/max_vel
        for i in range(3):
            if adjust_vel[i] > 1:
                adjust_vel[i] = 1
            if adjust_vel[i] < -1:
                adjust_vel[i] = -1
        return adjust_vel

    def set_target(self, target_vel):
        self.target_vel = target_vel

    def move_type(self):
        return "move"

class OpiManualMoveState(OpiPosState):
    def __init__(self, manual, opi_data):
        self.manual = manual
        self.data = opi_data
    
    def on_tick(self):
        return self.manual

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
    def on_tick(self, target_vel, opi_data):
        return [0, 0, 0]    # placeholder right now!

class OpiPosDriftState(OpiPosState):
    def on_tick(self, target_vel, opi_data):
        return [0, 0, 0]

class OpiRotateState(ABC):
    @abstractmethod
    def on_tick(): # returns thruster outputs for a single tick
        pass

class OpiRotMoveState(OpiRotateState):
    pass

class OpiAngleMoveState(OpiRotateState):
    pass

class OpiRotHoldState(OpiRotateState):
    pass

class OpiRotDriftState(OpiRotateState):
    def on_tick():
        pass

class ThrusterController:
    def __init__(self, delta_time=0.05):
        self.data = None
        self.pos_state = OpiPosMoveState()
        self.rotate_state = OpiRotDriftState()
        self.delta_time = delta_time
        self.mcu_interface = None
    
    # way to solve circular dependency
    def set_interface(self, mcu_interface):
        self.mcu_interface = mcu_interface

    def set_data(self, opi_data):
        self.data = opi_data

    # moves ROV based on input data
    def move_loop(self):
        while True:
            pos_thrust = self.pos_state.on_tick(self.delta_time)
            rot_thrust = self.rotate_state.on_tick(self.delta_time)
            # somehow integrate pos_thrust and rot_thrust
            
            time.sleep(self.delta_time)
            
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