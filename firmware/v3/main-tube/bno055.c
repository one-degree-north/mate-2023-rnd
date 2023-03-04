/* bno055.c
 * utilities to connect to one Bosch BNO055 IMU,
 * read all data, and categorize it into a usable form.
 */

#include "hardware/i2c.h"
#include "hardware/gpio.h"
#include "pico/stdlib.h"
#include <stdio.h>
#include "bno055.h"

// MODIFY THESE IF YOU AREN'T USING THE Adafruit RP2040 Feather!
#define BNO_SCL 3
#define BNO_SDA 2
#define BNO_I2C i2c1


static u8 bno_addr = 0x28;
static i2c_inst_t* bno_port = BNO_I2C;

float accel[3];
float mag[3];
float gyro[3];
float orientation[3];
float quaternion[4];
float linaccel[3];
float gravity[3];

u8 buf[58];

void bno_configure() {
    // this function contains our configuration.
    // refer to the datasheet to reconfigure.
    u8 config[2];

    // SYS_TRIGGER: internal oscillator, reset all interrupts, start self-test
    config[0] = 0x3F;
    config[1] = 0b01000001;
    i2c_write_blocking(bno_port, bno_addr, config, 2, true);

    // PWR_MODE: normal
    config[0] = 0x3E;
    config[1] = 0b00000000;
    i2c_write_blocking(bno_port, bno_addr, config, 2, true);

    // UNIT_SEL: m/s^2, uT, dps, degrees, Quaternion units, Celsius
    config[0] = 0x3B;
    config[1] = 0b00000000;
    i2c_write_blocking(bno_port, bno_addr, config, 2, true);

    // TEMP_SOURCE: from Gyroscope
    config[0] = 0x40;
    config[1] = 0b00000001;
    i2c_write_blocking(bno_port, bno_addr, config, 2, true);

    // AXIS_MAP_CONFIG: default
    config[0] = 0x41;
    config[1] = 0x24;
    i2c_write_blocking(bno_port, bno_addr, config, 2, true);

    // AXIS_MAP_SIGN: no change
    config[0] = 0x42;
    config[1] = 0b00000000;
    i2c_write_blocking(bno_port, bno_addr, config, 2, true);

    // OPR_MODE: IMU mode (accel, mag, gyro, orientation)
    config[0] = 0x3D;
    config[1] = 0b00001000;
    i2c_write_blocking(bno_port, bno_addr, config, 2, true);
}

bool bno_setup(u8 addr) {
    i2c_init(BNO_I2C, 400000); // Table 4-8
    gpio_set_function(BNO_SDA, GPIO_FUNC_I2C);
    gpio_set_function(BNO_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(BNO_SDA);
    gpio_pull_up(BNO_SCL);

    // bno_setup should be called only once, since it initializes bno_addr and bno_port
    sleep_ms(1);
    bno_addr = addr;
    bno_port = BNO_I2C;
    u8 reg = 0x00;
    u8 chipID[1];
    i2c_write_blocking(bno_port, bno_addr, &reg, 1, true);
    i2c_read_blocking(bno_port, bno_addr, chipID, 1, false);

    if (chipID[0] != 0xa0) {
        return false;
    }

    bno_configure();

    return true;
}

void bno_read() {
    // yes, we're literally just reading 58 bytes of data (the whole readable register)
    u8 reg = 0x00;
    i2c_write_blocking(bno_port, bno_addr, &reg, 1, true);
    i2c_read_blocking(bno_port, bno_addr, buf, 58, false);
}


// TODO: FIX VALUES, THEY CANT JUST BE TREATED AS SHORT 16 BIT INT
float* bno_accel() {
    i16 x = (buf[0x09] << 8) | buf[0x08];
    i16 y = (buf[0x0B] << 8) | buf[0x0A];
    i16 z = (buf[0x0D] << 8) | buf[0x0C];

    // 100 lower bits per m/s^2
    accel[0] = x / 100.0;
    accel[1] = y / 100.0;
    accel[2] = z / 100.0;

    return accel;
}

float* bno_magnet() {
    i16 x = (buf[0x0F] << 8) | buf[0x0E];
    i16 y = (buf[0x11] << 8) | buf[0x10];
    i16 z = (buf[0x13] << 8) | buf[0x12];

    // 16 lower bits per microtesla
    mag[0] = x / 16.0;
    mag[1] = y / 16.0;
    mag[2] = z / 16.0;

    return mag;
}

float* bno_gyro() {
    i16 x = (buf[0x15] << 8) | buf[0x14];
    i16 y = (buf[0x17] << 8) | buf[0x16];
    i16 z = (buf[0x19] << 8) | buf[0x18];

    // 16 lower bits per degree
    gyro[0] = x / 16.0;
    gyro[1] = y / 16.0;
    gyro[2] = z / 16.0;

    return gyro;
}

float* bno_orientation() {
    i16 yaw = (buf[0x1B] << 8) | buf[0x1A];
    i16 pitch = (buf[0x1D] << 8) | buf[0x1C];
    i16 roll = (buf[0x1F] << 8) | buf[0x1E];

    // 16 lower bits per degree
    orientation[0] = yaw / 16.0;
    orientation[1] = pitch / 16.0;
    orientation[2] = roll / 16.0;

    return gyro;
}

float* bno_quaternion() {
    i16 w = (buf[0x21] << 8) | buf[0x20];
    i16 x = (buf[0x23] << 8) | buf[0x22];
    i16 y = (buf[0x25] << 8) | buf[0x24];
    i16 z = (buf[0x27] << 8) | buf[0x26];

    // quaternions are unitless
    // technically should divide them by 2^14,
    // but accuracy is lost when using 32bit floats
    quaternion[0] = w;
    quaternion[1] = x;
    quaternion[2] = y;
    quaternion[3] = z;

    return quaternion;
}

float* bno_lin_accel() {
    i16 x = (buf[0x29] << 8) | buf[0x28];
    i16 y = (buf[0x2B] << 8) | buf[0x2A];
    i16 z = (buf[0x2D] << 8) | buf[0x2C];

    // 100 lower bits per m/s^2
    linaccel[0] = x / 100.0;
    linaccel[1] = y / 100.0;
    linaccel[2] = z / 100.0;

    return linaccel;
}

float* bno_gravity() {
    i16 x = (buf[0x2F] << 8) | buf[0x2E];
    i16 y = (buf[0x31] << 8) | buf[0x30];
    i16 z = (buf[0x33] << 8) | buf[0x32];

    // 100 lower bits per m/s^2
    gravity[0] = x / 100.0;
    gravity[1] = y / 100.0;
    gravity[2] = z / 100.0;

    return gravity;
}

float bno_temperature() {
    u8 temp = buf[0x34];
    // 1 lower bit per degree celsius
    return temp;
}

u8 bno_calibration() {
    return buf[0x35];
}

u8 bno_sys_status() {
    return buf[0x39];
}

u8 bno_sys_error() {
    return buf[0x3A];
}
