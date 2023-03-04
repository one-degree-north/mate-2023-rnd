#!/bin/bash
gcc -O3 esc_software_pwm_singlethread.c udp_comms.c -lwiringPi -lpthread -o thr_ctrl
