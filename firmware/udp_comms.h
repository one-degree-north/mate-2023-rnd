#ifndef INCLUDE_UDP_COMMS_H
#define INCLUDE_UDP_COMMS_H

#include "esc_software_pwm.h"

void* udp_thread(void* input);
void parse_data(int n, char* buf, thruster_t* thrusters);

#endif
