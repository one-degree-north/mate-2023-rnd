#ifndef INCLUDE_UDP_COMMS_H
#define INCLUDE_UDP_COMMS_H

#include "esc_software_pwm.h"

void* udp_thread(void* input);
<<<<<<< HEAD
void parse_data(int n, char* buf, thruster_t* thrusters);
=======
int setup_serial();
void parse_data(int n, char* buf, thruster_t* thrusters, int serial_port);
>>>>>>> 88096d4 (work changes: add udp, other stuff)

#endif
