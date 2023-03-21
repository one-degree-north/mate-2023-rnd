# Controls thruster movement
from abc import ABC, abstractmethod, abstractproperty
import time, threading
from collections import namedtuple
from data import *

move = namedtuple("move", ['f', 's', 'u', 'p', 'r', 'y'])

class PID:
    def __init__(self, p_const=1, i_const=1, d_const=1):
        self.p_const = p_const
        self.i_const = i_const
        self.d_const = d_const
        self.i = 0
        self.past_error = 0

    # update PID and get new value
    def on_tick(self, error, delta_time):
        # update integral
        self.i += error*delta_time
        return_value = self.p_const * error + self.i + self.d_const * (self.past_error-error)/delta_time
        self.past_error = error
        return return_value

    def change_const(self, p_const=1, i_const=1, d_const=1):
        self.p_const = p_const
        self.i_const = i_const
        self.d_const = d_const

class OpiPosState(ABC):
    @abstractmethod
    def on_tick(): # returns target forward, side, up movements (-1 to 1) for a single tick
        return [0, 0, 0]
    @abstractproperty
    def move_type():
        return "def"
    @abstractmethod
    def set_target():
        pass

# move with thruster values (-1 to 1)
class OpiPosManualState(OpiPosState):
    def __init__(self, manual):
        self.manual = manual
        self.move_type = "manual"
    
    def on_tick(self):
        return self.manual
    def set_target(self, manual):
        self.manual = manual

    def move_type(self):
        return "manual"

# move with target PID values
class OpiPosPidState(OpiPosState):
    def __init__(self, target_vel, opi_data, delta_time):
        self.target_vel = target_vel
        self.opi_data = opi_data
        self.pids = [PID(), PID(), PID()]
        self.delta_time = delta_time
        self.move_type = "pid"

    # returns roll, pitch, yaw thrusts (-1 to 1)
    def on_tick(self):
        return_thrusts = [0, 0, 0]
        for i in range(3):
            return_thrusts[i] = self.pids[i].on_tick(self.target_vel-self.opi_data.vel[i], self.delta_time)
        return return_thrusts

    def set_target(self, target_vel):
        self.target_vel = target_vel

    def move_type(self):
        return "pid"

# pid with all target velocities 0
class OpiPosHoldState(OpiPosState):
    def __init__(self, opi_data, delta_time):
        self.target_vel = [0, 0, 0]
        self.data = opi_data
        self.pids = [PID(), PID(), PID()]
        self.delta_time = delta_time
        self.move_type = "hold"

    # returns roll, pitch, yaw thrusts (-1 to 1)
    def on_tick(self):
        return_thrusts = [0, 0, 0]
        for i in range(3):
            return_thrusts[i] = self.pids[i].on_tick(self.target_vel-self.opi_data.vel[i], self.delta_time)
        return return_thrusts

    def set_target(self):
        pass

    def move_type(self):
        return "hold"

# no thruster movement
class OpiPosDriftState(OpiPosState):
    def __init__(self):
        self.move_type = "drift"
    def on_tick(self):
        return [0, 0, 0]
    
    def set_target(self):
        pass

    def move_type(self):
        return "drift"

class OpiRotateState(ABC):
    @abstractmethod
    def on_tick(): # returns thruster outputs for a single tick
        pass

# roll, pitch, yaw values from -1 to 1
class OpiRotManualState(OpiRotateState):
    def __init__(self, manual):
        self.manual = manual
        self.move_type = "manual"
    
    def on_tick(self):
        return self.manual

    def set_target(self, manual):
        self.manual = manual

    def move_type(self):
        return "manual"

# pid with target angle (eulers as of now)
class OpiRotAngleState(OpiRotateState):
    def __init__(self, target_eul, opi_data, delta_time):
        self.target_eul = target_eul
        self.opi_data = opi_data
        self.delta_time = delta_time
        self.pids = [PID(), PID(), PID()]
        self.move_type = "angle"

    def on_tick(self):
        return_thrusts = [0, 0, 0]
        for i in range(3):
            # angle error!, TODO: CHECK IF THIS ACTUALLY WORKS
            error = self.target_eul[i] - self.opi_data.eul[i]
            error = (error + 180)%360-180
            return_thrusts[i] = self.pids[i].on_tick(error, self.delta_time)
    
    def set_target(self, target_eul):
        self.target_eul = target_eul

    def move_type(self):
        return "angle"

# pid using gyroscope with target rotation (rad/s)
class OpiRotVelState(OpiRotateState):
    def __init__(self, target_vel, opi_data, delta_time):
        self.target_vel = target_vel
        self.opi_data = opi_data
        self.delta_time = delta_time
        self.pids = [PID(), PID(), PID()]
        self.move_type = "gyro"

    def on_tick(self):
        return_thrusts = [0, 0, 0]
        for i in range(3):
            return_thrusts[i] = self.pids[i].on_tick(self.target_vel[i] - self.opi_data.gyro[i], self.delta_time)
    
    def set_target(self, target_vel):
        self.target_vel = target_vel

    def move_type(self):
        return "gyro"

class OpiRotHoldState(OpiRotateState):
    def __init__(self, opi_data, delta_time):
        self.target_vel = [0, 0, 0]
        self.opi_data = opi_data
        self.delta_time = delta_time
        self.pids = [PID(), PID(), PID()]
        self.move_type = "hold"

    def on_tick(self):
        return_thrusts = [0, 0, 0]
        for i in range(3):
            return_thrusts[i] = self.pids[i].on_tick(self.target_vel[i] - self.opi_data.gyro[i], self.delta_time)
    
    def set_target(self, target_vel):
        pass

    def move_type(self):
        return "hold"

# no thruster movements at  all (equivalent to manual state of all 0)
class OpiRotDriftState(OpiRotateState):
    def __init__(self):
        self.move_type = "drift"

    def on_tick(self):
        return [0, 0, 0]
    
    def set_target(self, target_vel):
        pass

    def move_type(self):
        return "drift"

class ThrusterController:
    def __init__(self, move_delta_time=0.05):
        self.data = None
        self.pos_state = OpiPosDriftState()
        self.rot_state = OpiRotDriftState()
        self.move_delta_time = move_delta_time
        self.mcu_interface = None
        self.max_thrust = 0.5   # maximum thruster value allowed (0 to 1)

    # way to solve circular dependency
    def set_interface(self, mcu_interface):
        self.mcu_interface = mcu_interface

    def set_data(self, opi_data):
        self.data = opi_data

    def start_loop(self):
        move_thread = threading.Thread(target=self.move_loop, daemon=True)
        move_thread.start()
    
    def start_debug_loop(self):
        move_thread = threading.Thread(target=self.debug_loop, daemon=True)
        move_thread.start()

    def debug_loop(self):
        while True:
            pos_thrust = self.pos_state.on_tick()
            rot_thrust = self.rot_state.on_tick()
            # TODO: Revise and check if this actually is an ok way to do this
            # somehow integrate pos_thrust and rot_thrust
            # transform forward, side, up, pitch, roll, yaw to thruster speeds
            mov = move(*pos_thrust, *rot_thrust) # simplified thrusters with f, s, u, p, r, y
            total_thrust = [0, 0, 0, 0, 0, 0, 0, 0]
            total_thrust[0] = mov.f - mov.s - mov.y
            total_thrust[1] = mov.f + mov.s + mov.y
            total_thrust[2] = mov.f - mov.s + mov.y
            total_thrust[3] = mov.f + mov.s - mov.y

            total_thrust[4] = mov.u + mov.p - mov.r
            total_thrust[5] = mov.u + mov.p + mov.r
            total_thrust[6] = mov.u - mov.p + mov.r
            total_thrust[7] = mov.u - mov.p - mov.r

            print(f"total thrust before processing: {total_thrust}")
            # get maximum thrust present after adding
            max_thrust = 0
            for i in range(8):
                max_thrust = abs(total_thrust[i])
            
            # scale all thrust values down baesd on the maximum thrust
            if max_thrust > self.max_thrust:
                for i in range(8):
                    # adjust for maximum thrust present
                    total_thrust[i] = int(total_thrust[i] / max_thrust)*self.max_thrust
                    # adjust for microseconds (-1 to 1) to (1000 to 2000)
                    total_thrust[i] = 1500 + 500*total_thrust[i]
            
                    # last adjustment in case total_thrust[i] was above maximum thrust or minmum thrust
                    lowest = 1500 - self.max_thrust*500 
                    highest = self.max_thrust*500+1500
                    if total_thrust[i] < lowest:
                        total_thrust[i] = lowest
                    if total_thrust[i] > highest:
                        total_thrust[i] = highest
            else:
                for i in range(8):
                    # adjust for maximum thrust present
                    total_thrust[i] = int(total_thrust[i])*self.max_thrust
                    # adjust for microseconds (-1 to 1) to (1000 to 2000)
                    total_thrust[i] = 1500 + 500*total_thrust[i]

                    # last adjustment in case total_thrust[i] was above maximum thrust or minmum thrust
                    lowest = 1500 - self.max_thrust*500 
                    highest = self.max_thrust*500+1500
                    if total_thrust[i] < lowest:
                        total_thrust[i] = lowest
                    if total_thrust[i] > highest:
                        total_thrust[i] = highest

            # move with all thrusts
            print(f"writing thrust: {total_thrust}")
            # self.mcu_interface.set_thruster(total_thrust)
            time.sleep(self.move_delta_time)

    # moves ROV based on input data
    def move_loop(self):
        while True:
            pos_thrust = self.pos_state.on_tick()
            rot_thrust = self.rot_state.on_tick()
            # TODO: Revise and check if this actually is an ok way to do this
            # somehow integrate pos_thrust and rot_thrust
            # transform forward, side, up, pitch, roll, yaw to thruster speeds
            mov = move(*pos_thrust, *rot_thrust) # simplified thrusters with f, s, u, p, r, y
            total_thrust = [0, 0, 0, 0, 0, 0, 0, 0]
            total_thrust[0] = mov.f - mov.s - mov.y
            total_thrust[1] = mov.f + mov.s + mov.y
            total_thrust[2] = mov.f - mov.s + mov.y
            total_thrust[3] = mov.f + mov.s - mov.y

            total_thrust[4] = mov.u + mov.p - mov.r
            total_thrust[5] = mov.u + mov.p + mov.r
            total_thrust[6] = mov.u - mov.p + mov.r
            total_thrust[7] = mov.u - mov.p - mov.r

            # get maximum thrust present after adding
            max_thrust = 0
            for i in range(8):
                max_thrust = abs(total_thrust[i])
            
            # scale all thrust values down baesd on the maximum thrust
            if max_thrust > self.max_thrust:
                for i in range(8):
                    # adjust for maximum thrust present
                    total_thrust[i] = int(total_thrust[i] / max_thrust)*self.max_thrust
                    # adjust for microseconds (-1 to 1) to (1000 to 2000)
                    total_thrust[i] = 1500 + 500*total_thrust[i]
            
                    # last adjustment in case total_thrust[i] was above maximum thrust or minmum thrust
                    lowest = 1500 - self.max_thrust*500 
                    highest = self.max_thrust*500+1500
                    if total_thrust[i] < lowest:
                        total_thrust[i] = lowest
                    if total_thrust[i] > highest:
                        total_thrust[i] = highest
            else:
                for i in range(8):
                    # adjust for maximum thrust present
                    total_thrust[i] = int(total_thrust[i])*self.max_thrust
                    # adjust for microseconds (-1 to 1) to (1000 to 2000)
                    total_thrust[i] = 1500 + 500*total_thrust[i]

                    # last adjustment in case total_thrust[i] was above maximum thrust or minmum thrust
                    lowest = 1500 - self.max_thrust*500 
                    highest = self.max_thrust*500+1500
                    if total_thrust[i] < lowest:
                        total_thrust[i] = lowest
                    if total_thrust[i] > highest:
                        total_thrust[i] = highest
            
            # move with all thrusts
            self.mcu_interface.set_thruster(total_thrust)
            time.sleep(self.move_delta_time)

    # set all manual microseconds (1000 to 2000)
    def set_raw_thrust(self, thrusts):
        pass

    # set manual move (-1 to 1)
    def set_pos_manual(self, moves):
        if self.pos_state.move_type == "manual":
            self.pos_state.set_target(moves)
        else:
            self.pos_state = OpiPosManualState(moves)

    #set target velocity
    def set_pos_target_vel(self, vels):
        if self.pos_state.move_type == "pid":
            self.pos_state.set_target(vels)
        else:
            self.pos_state = OpiPosPidState(vels, self.data.data, self.move_delta_time)

    # hold (pid)
    def set_pos_hold(self):
        self.pos_state = OpiPosHoldState()

    def set_pos_drift(self):
        self.pos_state = OpiPosDriftState()


    # set manual rotation (-1 to 1)
    def set_rot_manual(self, thrusts):
        if self.rot_state.move_type == "manual":
            self.rot_state = OpiRotManualState(thrusts)
        else:
            self.rot_state.set_target(thrusts)

    # set target angular velocity
    def set_rot_vel(self, vels):
        if self.rot_state.move_type == "gyro":
            self.rot_state.set_target(vels)
        else:
            self.rot_state = OpiRotVelState(vels, self.data.data, self.move_delta_time)
    
    #set target rotational angle
    def set_rot_angle(self, angles):
        if self.rot_state.move_type == "angle":
            self.rot_state.set_target(angles)
        else:
            self.rot_state = OpiRotAngleState(angles, self.data.data, self.move_delta_time)

    def set_rot_hold(self):
        self.rot_state = OpiRotHoldState()
    
    def set_rot_drift(self):
        self.rot_state = OpiRotDriftState()
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
if __name__ == "__main__":
    thruster_controller = ThrusterController()
    data = OpiDataProcess()
    thruster_controller.set_data(data)
    data.start_bno_reading()
    thruster_controller.start_debug_loop()
    while True:
        val = input("pos / rot> ")
        type = input("type > ")
        target = input("thrusts> ").split()
        thrusts = []
        for tar in target:
            thrusts.append(float(tar))
        if val == "pos" and type == "manual":
            thruster_controller.set_pos_manual(thrusts)
        if val == "pos" and type == "pid":
            thruster_controller.set_pos_target_vel(thrusts)
        if val == "rot" and type == "manual":
            thruster_controller.set_rot_manual(thrusts)
        if val == "rot" and type == "angle":
            thruster_controller.set_rot_angle(thrusts)
        if val == "rot" and type == "gyro":
            thruster_controller.set_rot_vel(thrusts)