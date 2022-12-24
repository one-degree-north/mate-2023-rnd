When number ranges are given, both numbers are inclusive!
### Unity is opened, continuously asks to establish connection until closed.\ Python confirms connection, then it can proceed. Both sides can close the connection (just quiting Unity or termination the program would cause problems. Maybe there is a built in solution to this though.).
### I personally want to offload as much as possible to the python side so Unity is more of an interface with VR.
### Currently using UDP, may change to pipes if we want to though.
# Unity -> Python
### Goals:
- send vr data:/
    - head position
    - controller position (?)
    - ultrealeap data
    - report configuration
- ask to establish connection
- confirm connection establishment (?)
- close connection

### Packet Format:
| Data type | byte 0 | bytes 1-4 | bytes 5-8 | bytes 9 - 12 |
| --- | --- | --- | --- | --- |
| ask to establish connection | 0x01 |
| close connection | 0x10 | 
| headset position | 
| headset rotation (degrees) |
| headset rotation (quaternions) | 
| send all data (when not set to only send on data change) |

# Python -> Unity
Goals:/
- update view
- change configuration
- haptic feedback?
- open connection
- close connection

### Packet Format:
| Data type | byte 0 | bytes 1-4 | bytes 5-8 | bytes 9-12 |