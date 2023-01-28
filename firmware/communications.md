# Overview of communications (integrety and length of packets should be managed by canbus)
Note: I'm not too sure if this is appropriate, but I am currently using canbus IDs like commands, (IDs cannot be sent by two senders at the same time)
CAN bus packet ID: 11 bits
CAN bus packet max size: 8 bytes
Low ID numbers have a higher priority (PROBABLY INCORPORATE THIS!!!, REDUCE PRIORITY OF RETURN DATA?)
## CANBUS packet ID (11 bits):
(numbers are inclusive with both bottom and upper)

### Bits (for packet ID):
0-2: sending device\
3-5: receiving device\
6-10: command (or data type in sending data, see list of commands below)\

### Devices:
000: main-tube\
001: right arm\
010: left arm\
011: onshore device\

### Command format:
## Sending data (ROV -> onshore)

### Commands for control station (return data)
Value in packet will be a single float\
Command bits 0-2: specifies the data type (orientation, gyro, etc.)\
Command bits 3-4: specifies the axis (eg. front, side, up). The value in axis will be big endian (SUBJECT TO CHANGE) in order of it being given (eg. an axis of x, y, z would have 00 as x, 01 as y, and 10 as z).\
| data value |  command BITS 0-4 | axis BITS 5-6| packet BYTES 0-3 | packet BYTES 4 |
| --- | --- | --- | --- | --- |
| orientation| 0x01 | r, p, y | float, orientation |
| gyro data | 0x02 | r, p, y | float, gyro |
| acceleration data | 0x03 | x, y, z | float, accel |
| quaternion data | 0x04 | ?? | float, quaternion |
| settings | 0x04 | none (default 00) | int, sensor send rate (in 10s of ms) | bool, pid enabled |
| error1 | 0x05 | f, s, u | float, error |
| error2 | 0x06 | r, p, y | float, error |

## Acting on command (onshore -> ROV)
### Commands for main tube
NOTE: Writing NO PID commands will disable using PID and instead switch to regular thrust (all existing PID targets will be set to 0)\
| command description | command id | byte values |
| --- | --- | --- |
| set settings | 0x01 |
| front accel (pid) | 0x0A | float, accel |
| side accel (pid) | 0x0B | float, accel
| up accel (pid) | 0x0C | float, accel |
| roll accel (pid) | 0x0D | float, accel |
| pitch accel (pid) | 0x0E | float, accel |
| yaw accel (pid) | 0x0F | float, accel |
| front thrust (no pid) | 0x10 | float, percent |
| side thrust (no pid) | 0x11 | float, percent |
| up thrust (no pid) | 0x12 | float, percent |
| roll accel (pid) | 0x13 | float, percent |
| pitch accel (pid) | 0x14 | float, percent |
| yaw accel (pid) | 0x15 | float, percent |

### Commands for arm tube
