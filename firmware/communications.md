### Overview: integrety and length of packets should be managed by canbus
Note: I'm not too sure if this is appropriate, but I am currently using canbus IDs like commands, (IDs cannot be sent by two senders at the same time)
### CANBUS packet ID (11 bits):
(inclusive with both bottom and upper)
## Devices:
# 00: main-tube
# 01: right arm
# 10: left arm
# 11: onshore device

# 0-1: sending device
# 2-3: receiving device
# 4-10: command (or data type in sending data)

### Command format:
## Sending data (ROV -> onshore)
(in bytes (max 8 bytes))
# 0-3: data value (all values floats)

## Acting on command (onshore -> ROV)
Depends on command

### Commands for control station (return data)
| data value | command id | byte values |
| --- | --- | --- |
| orientation data (r, p, y)    |
| gyro data (r, p, y)           |
| acceleration data (x, y, z)   |

### Commands for main tube
| command description | command id | byte values |
| --- | --- | --- |
| 

### Commands for arm tube
