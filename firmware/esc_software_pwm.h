#ifndef INCLUDE_ESC_SOFTWARE_PWM_H
#define INCLUDE_ESC_SOFTWARE_PWM_H

#include <stdint.h>

#define NUM_THRUSTERS 8

#define u8 uint8_t
#define u16 uint16_t

typedef struct Thruster {
    u8 enable;      // 0 if disabled
    u8 pin;         // board pin according to wiringPi
    u16 target;     // target pulse in us (1000-1800)
    u16 current;    // current pulse in us (1000-1800)
} thruster_t;

void setup();

void loop();

void* write_cycle(void* input);

void write_one(uint8_t i, uint16_t ms_on);
void write_all(uint16_t ms_on);

void* update_cycle(void* input);

#endif
