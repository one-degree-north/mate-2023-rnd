# Controls thruster movement
from abc import ABC, abstractmethod, abstractproperty
import time

class OpiPosState(ABC):
    @abstractmethod
    def on_tick(): # returns thruster outputs for a single tick
        pass

class OpiPosMoveState(OpiPosState):
    def __init__(self, target_vel):
        self.target_vel = target_vel
    
    def on_tick(self, data):
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

class OpiPosHoldState(OpiPosState):
    def on_tick(target_vel, data):
        return [0, 0, 0]    # placeholder right now!

class OpiPosDriftState(OpiPosState):
    def on_tick(target_vel, data):
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
    pass

class ThrusterController:
    def __init__(self):
        self.data
        self.pos_state
        self.rotate_state

    # moves ROV based on input data
    def move_loop(self):
        while True:
            pos_thrust = self.pos_state.on_tick()
            rot_thrust = self.rotate_state.on_tick()

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