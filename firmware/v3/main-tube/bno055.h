#ifndef BNO055_H_
#define BNO055_H_

#include "int_shorthand.h"

bool bno_setup(u8 addr);
void bno_configure();
void bno_read();
float* bno_accel();
float* bno_magnet();
float* bno_gyro();
float* bno_orientation();
float* bno_quaternion();
float* bno_lin_accel();
float* bno_gravity();
float bno_temperature();
u8 bno_calibration();
u8 bno_sys_status();
u8 bno_sys_error();
void bno_accel_offset(float x, float y, float z);
void bno_magnet_offset(float x, float y, float z);
void bno_gyro_offset(float x, float y, float z);
void bno_accel_radius(float r);
void bno_magnet_radius(float r);

#endif // #ifndef BNO055_H_

