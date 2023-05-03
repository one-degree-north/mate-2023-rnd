from vpython import *
from thruster_utils import *
from pid_utils import *

#15.5 19.5 36 39.5

thrusters = [
    cylinder(pos=vector(7.75, 0, 9.75)*.01, axis=vector(0, .05, 0), color=vector(0, 0, 1), radius=0.04),
    cylinder(pos=vector(7.75, 0, -9.75)*.01, axis=vector(0, .05, 0), color=vector(0, 0, 1), radius=0.04),
    cylinder(pos=vector(-7.75, 0, 9.75)*.01, axis=vector(0, .05, 0), color=vector(0, 0, 1), radius=0.04),
    cylinder(pos=vector(-7.75, 0, -9.75)*.01, axis=vector(0, .05, 0), color=vector(0, 0, 1), radius=0.04),
    cylinder(pos=vector(18, 0, 19.75)*.01, axis=vector(.035, 0, -.035), color=vector(1, 0, 1), radius=0.04),
    cylinder(pos=vector(18, 0, -19.75)*.01, axis=vector(.035, 0, .035), color=vector(1, 0, 1), radius=0.04),
    cylinder(pos=vector(-18, 0, 19.75)*.01, axis=vector(-.035, 0, -.035), color=vector(1, 0, 1), radius=0.04),
    cylinder(pos=vector(-18, 0, -19.75)*.01, axis=vector(-.035, 0, .035), color=vector(1, 0, 1), radius=0.04)
]

body = cylinder(pos=vector(-.15, 0, 0), axis=vector(.30, 0, 0), radius=0.06, color=vector(.7, .7, .7))
rov = compound([body, center, *thrusters])

mass = 3 # kg
moi = 0.35 * mass * 0.26 * 0.26 # kg * m^2

kp_rot = 1
ki_rot = 1.5
kd_rot = 0
pid_rot = {
    'yaw': PIDController(kp_pos, ki_pos, kd_pos),
    'pitch': PIDController(kp_pos, ki_pos, kd_pos),
    'roll': PIDController(kp_pos, ki_pos, kd_pos)
}

t = 0
dt = 0.05
rot = rov.axis
target_rot = vector(0  , 0, 1)

while True:
    rate(1/dt)
    rot = rov.axis

    pitch_rot = vector(rot.x, 0, rot.z)
    yaw_target = vector(target_rot.x, 0, target_rot.z)
    dpitch =


    t += dt
