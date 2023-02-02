#ifndef INCLUDE_ESC_SOFTWARE_PWM_H
#define INCLUDE_ESC_SOFTWARE_PWM_H

void setup();

void loop();

void* write_cycle(void* input);

void write_one(uint8_t i, uint16_t ms_on);
void write_all(uint16_t ms_on);

void* update_cycle(void* input);

#endif
