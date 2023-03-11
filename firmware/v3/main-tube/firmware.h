// firmware.h
// v3 - orangepi uart5 <---> oneshot & bno055
#ifndef INCLUDE_FIRMWARE_H
#define INCLUDE_FIRMWARE_H

#include "int_shorthand.h"

/*** GENERAL ***/
void soft_halt();
void halt();
void reset();

void setup();
void loop();

/*** COMMANDS ***/
void cmd_test(u8 len, u8 *data);
void cmd_reset(u8 len, u8 *data);
void cmd_halt(u8 len, u8 *data);

void cmd_set_thruster(u8 param, u8 len, u8 *data);
void cmd_set_thruster_mask(u8 param, u8 len, u8 *data);
void cmd_get_thruster(u8 param, u8 len, u8 *data);

void cmd_get_sensor(u8 param, u8 len, u8 *data);

/*** COMMAND RESPONSES ***/
void cmd_return_hello();
void cmd_return_echo(u8 len, u8 *data);

void cmd_return_thruster(u8 idx);
void cmd_return_all_thrusters();

void cmd_return_vec3(u8 param, float* x, float* y, float* z);
void cmd_return_quaternion(u8 param, float* w, float* x, float* y, float* z);
void cmd_return_int(u8 param, u16 data);

/*** COMMUNICATIONS ***/
#define UART_BAUD 115200
#define UART_QUEUE_SIZE 40  // max 256
#define UART_HEADER 0xa7
#define UART_FOOTER 0x7a
#define UART_PIN_RX 1
#define UART_PIN_TX 28      // A2 on the rp2040 feather
#define UART_MAX_PACKET_LENGTH 48

void uart_setup();
void uart_reset_queue();
void uart_read_byte(u8 c);
void uart_parse_packet();
void uart_parse_byte(u8 c);
void uart_read();
void uart_write(u8* data, u8 length);

/*** THRUSTERS ***/
#define MAX_DELTA_POS 2000 // delta us per second, TODO: replace with optimal solution on thrust curve
#define NUM_THRUSTERS 8
const u8 thruster_pins[] = {12, 11, 10, 9, 24, 25, 18, 19};
u16 thruster_pos[NUM_THRUSTERS];
u16 thruster_target_pos[NUM_THRUSTERS];
u64 thruster_prev_loop_us;

void thruster_init_oneshot(u8 pin);
void thruster_output(u8 thruster, u16 level);
void thruster_set_target(u8 thruster, u16 level);
void thruster_set_value(u8 thruster, u16 level);
void setup_outputs();
void loop_outputs();

/*** BNO055 INTERFACE ***/
#define I2C_PORT i2c1
#define BNO055_ADDR 0x28

#endif // #ifndef INCLUDE_FIRMWARE_H
