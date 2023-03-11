// firmware.c
// v3 - orangepi uart5 <---> oneshot & bno055
#include "hardware/adc.h"
#include "hardware/gpio.h"
#include "hardware/i2c.h"
#include "hardware/irq.h"
#include "hardware/pwm.h"
#include "hardware/uart.h"
#include "pico/stdlib.h"
#include "pico/binary_info.h"
#include <stdio.h>

#include "int_shorthand.h"
#include "utils.h"

#include "bno055.h"
#include "firmware.h"


/*** GENERAL ***/

void soft_halt() {
    for (int i = 0; i < NUM_THRUSTERS; ++i) {
        thruster_set_target(i, 1500);
    }
    loop_outputs();
}

void halt() {
    for (int i = 0; i < NUM_THRUSTERS; ++i) {
        thruster_set_target(i, 1500);
        thruster_set_value(i, 1500);
    }
    loop_outputs();
}

void reset() {
    halt();
    // maybe reset uart too
}

void setup() {
    setup_outputs();
    //bno_setup(BNO055_ADDR);
    //bno_configure();
    uart_setup();

    // LED on 13
    gpio_init(13);
    gpio_set_dir(13, GPIO_OUT);
    gpio_put(13, 1);
}

void loop() {
    //bno_read();
    //uart_read(); - replaced by interrupts
    loop_outputs();
    tight_loop_contents(); // not sure what this does
}

/*** COMMANDS ***/
void cmd_test(u8 len, u8 *data) {
    if (len == 0)
        cmd_return_hello();
    else
        cmd_return_echo(len, data);
}
void cmd_reset(u8 len, u8 *data) {
    reset();
}

void cmd_halt(u8 len, u8 *data) {
    soft_halt();
}

void cmd_set_thruster(u8 param, u8 len, u8 *data) {
    if ((param < 0x00 || param > NUM_THRUSTERS) && param != 0x0F)
        return;

    if (len == 2) {
        u16 val = data[0] * 0x100 + data[1];
        thruster_set_target(param, val);
    }

    if (len == 16) {
        for (int i = 0; i < 8; ++i) {
            u16 val = data[i * 2] * 0x100 + data[i * 2 + 1];
            thruster_set_target(i, val);
        }
    }
}

void cmd_set_thruster_mask(u8 param, u8 len, u8 *data) {
    if (len == 2) {
        u8 param_ptr = param;
        u16 val = data[0] * 0x100 + data[1];

        for (int i = 0; i < 8; ++i) {
            param_ptr >>= 1;
            if (param_ptr & 0b1) {
                thruster_set_target(i, val);
            }
        }
    }
}

void cmd_get_thruster(u8 param, u8 len, u8 *data) {
    if ((param < 0x00 || param > NUM_THRUSTERS) && param != 0x0F)
        return;

    if (param == 0x0F) return cmd_return_all_thrusters();
    else return cmd_return_thruster(param);
}

void cmd_get_sensor(u8 param, u8 len, u8 *data) {
    if (param < 0x30 || param > 0x3F || param == 0x3D)
        return;

    switch (param) {
        case 0x31: {
            float* accel = bno_accel();
            cmd_return_vec3(param, &accel[0], &accel[1], &accel[2]);
            break;
        }
        case 0x32: {
            float* mag = bno_magnet();
            cmd_return_vec3(param, &mag[0], &mag[1], &mag[2]);
            break;
        }
        case 0x33: {
            float* gyro = bno_gyro();
            cmd_return_vec3(param, &gyro[0], &gyro[1], &gyro[2]);
            break;
        }
        case 0x34: {
            float* orientation = bno_orientation();
            cmd_return_vec3(param, &orientation[0], &orientation[1], &orientation[2]);
            break;
        }
        case 0x35: {
            float* quaternion = bno_quaternion();
            cmd_return_quaternion(param, &quaternion[0], &quaternion[1], &quaternion[2], &quaternion[3]);
            break;
        }
        case 0x36: {
            float* linaccel = bno_lin_accel();
            cmd_return_vec3(param, &linaccel[0], &linaccel[1], &linaccel[2]);
            break;
        }
        case 0x37: {
            float* gravity = bno_gravity();
            cmd_return_vec3(param, &gravity[0], &gravity[1], &gravity[2]);
            break;
        }
        case 0x38: {
            u16 calibration = bno_calibration();
            cmd_return_int(param, calibration);
            break;
        }
        case 0x39: {
            u16 bno_system = (bno_sys_status() << 8) | bno_sys_error();
            cmd_return_int(param, bno_system);
            break;
        }
        case 0x3A: {
            cmd_return_int(param, bno_temperature());
            break;
        }
        case 0x3F: {
            // literally everything above
            // c switch case is annoying though
            float* accel = bno_accel();
            cmd_return_vec3(param, &accel[0], &accel[1], &accel[2]);
            float* mag = bno_magnet();
            cmd_return_vec3(param, &mag[0], &mag[1], &mag[2]);
            float* gyro = bno_gyro();
            cmd_return_vec3(param, &gyro[0], &gyro[1], &gyro[2]);
            float* orientation = bno_orientation();
            cmd_return_vec3(param, &orientation[0], &orientation[1], &orientation[2]);
            float* quaternion = bno_quaternion();
            cmd_return_quaternion(param, &quaternion[0], &quaternion[1], &quaternion[2], &quaternion[3]);
            float* linaccel = bno_lin_accel();
            cmd_return_vec3(param, &linaccel[0], &linaccel[1], &linaccel[2]);
            float* gravity = bno_gravity();
            cmd_return_vec3(param, &gravity[0], &gravity[1], &gravity[2]);
            u16 calibration = bno_calibration();
            cmd_return_int(param, calibration);
            u16 bno_system = (bno_sys_status() << 8) | bno_sys_error();
            cmd_return_int(param, bno_system);
            cmd_return_int(param, bno_temperature());
            break;
        }
        default:
            break;
    }
}

/*** COMMAND RESPONSES ***/
void cmd_return_hello() {
    u8 bytes[] = {
        0x00, 0x00, 5,
        'h', 'e', 'l', 'l', 'o'
    };
    uart_write(bytes, 8);
}

void cmd_return_echo(u8 len, u8 *data) {
    uart_putc(uart0, UART_HEADER);
    uart_putc(uart0, 0x00);
    uart_putc(uart0, 0x00);
    uart_putc(uart0, len);
    for (int i = 0; i < len; ++i) {
        uart_putc(uart0, data[i]);
    }
    uart_putc(uart0, UART_FOOTER);
}

void cmd_return_thruster(u8 idx) {
    u8* ptr = (u8*) &thruster_pos[idx];

    u8 bytes[] = {
        0x1a, idx, 2,
        ptr[0], ptr[1]
    };
    uart_write(bytes, 5);
}

void cmd_return_all_thrusters() {
    u8* t0 = (u8*) &thruster_pos[0];
    u8* t1 = (u8*) &thruster_pos[1];
    u8* t2 = (u8*) &thruster_pos[2];
    u8* t3 = (u8*) &thruster_pos[3];
    u8* t4 = (u8*) &thruster_pos[4];
    u8* t5 = (u8*) &thruster_pos[5];
    u8* t6 = (u8*) &thruster_pos[6];
    u8* t7 = (u8*) &thruster_pos[7];

    u8 bytes[] = {
        0x1a, 0x1f, 16,
        t0[0], t0[1], t1[0], t1[1], t2[0], t2[1], t3[0], t3[1], t4[0], t4[1], t5[0], t5[1], t6[0], t6[1], t7[0], t7[1]
    };
    uart_write(bytes, 19);
}

void cmd_return_float(u8 param, float* data) {
    u8* ptr = (u8*) data;

    u8 bytes[] = {
        0x33, param, 4,
        ptr[0], ptr[1], ptr[2], ptr[3]
    };
    uart_write(bytes, 7);
}

void cmd_return_vec3(u8 param, float* x, float* y, float* z) {
    u8* x_ptr = (u8*) x;
    u8* y_ptr = (u8*) y;
    u8* z_ptr = (u8*) z;

    u8 bytes[] = {
        0x33, param, 12,
        x_ptr[0], x_ptr[1], x_ptr[2], x_ptr[3],
        y_ptr[0], y_ptr[1], y_ptr[2], y_ptr[3],
        z_ptr[0], z_ptr[1], z_ptr[2], z_ptr[3]
    };
    uart_write(bytes, 15);
}

void cmd_return_quaternion(u8 param, float* w, float* x, float* y, float* z) {
    u8* w_ptr = (u8*) w;
    u8* x_ptr = (u8*) x;
    u8* y_ptr = (u8*) y;
    u8* z_ptr = (u8*) z;

    u8 bytes[] = {
        0x33, param, 16,
        w_ptr[0], w_ptr[1], w_ptr[2], w_ptr[3],
        x_ptr[0], x_ptr[1], x_ptr[2], x_ptr[3],
        y_ptr[0], y_ptr[1], y_ptr[2], y_ptr[3],
        z_ptr[0], z_ptr[1], z_ptr[2], z_ptr[3]
    };
    uart_write(bytes, 19);
}

void cmd_return_int(u8 param, u16 data) {
    u8 upper = data / 0x100;
    u8 lower = data % 0x100;
    u8 bytes[] = {
        0x33, param, 2,
        upper, lower
    };
    uart_write(bytes, 5);
}

/*** COMMUNICATIONS ***/
u8 uart_queue[256];
u8 uart_queue_index = 0;
u8 uart_packet_length = 0;

void uart_setup() {
    uart_init(uart0, UART_BAUD);

    gpio_set_function(UART_PIN_RX, GPIO_FUNC_UART);
    gpio_set_function(UART_PIN_TX, GPIO_FUNC_UART);

    // disable cts/rts
    uart_set_hw_flow(uart0, false, false);

    // create interrupt
    irq_set_exclusive_handler(UART0_IRQ, uart_read);
    irq_set_enabled(UART0_IRQ, true);

    // enable UART interrupts for RX
    uart_set_irq_enables(uart0, true, false);

    // say hi
    cmd_return_hello();
}

void uart_reset_queue() {
    uart_queue_index = 0;
    uart_packet_length = 0;
}

void uart_read_byte(u8 c) {
    uart_queue[uart_queue_index] = c;
    uart_queue_index ++;
    uart_queue_index %= UART_QUEUE_SIZE;
}

void uart_parse_packet() {
    if (uart_queue[0] != UART_HEADER) return;

    u8 cmd = uart_queue[1];
    u8 param = uart_queue[2];
    u8 len = uart_queue[3];
    u8* data = uart_queue + 4;

    switch (cmd) {
        case 0x00:
            cmd_test(len, data);
            break;
        case 0x01:
            cmd_reset(len, data);
            break;
        case 0x03:
            cmd_halt(len, data);
            break;
        case 0x18:
            cmd_set_thruster(param, len, data);
            break;
        case 0x19:
            cmd_set_thruster_mask(param, len, data);
            break;
        case 0x1A:
            cmd_get_thruster(param, len, data);
            break;
        case 0x32:
            cmd_get_sensor(param, len, data);
            break;
        default:
            break;
    }
}

void uart_parse_byte(u8 c) {
    if (uart_queue_index == 3) {
        // len
        uart_packet_length = 5 + c;
        // if declared length is too long, discard
        if (uart_packet_length > 20) {
            uart_reset_queue();
            return;
        }
    }

    if (uart_queue_index == uart_packet_length - 1) {
        // footer
        if (c == UART_FOOTER) {
            uart_parse_packet();
        }
        uart_reset_queue();
        return;
    }

    uart_read_byte(c);
}

void uart_read() {
    while (uart_is_readable(uart0)) {
        u8 c = uart_getc(uart0);

        if (uart_queue_index != 0 || c == UART_HEADER) {
            uart_parse_byte(c);
        }
    }
}

void uart_write(u8* data, u8 length) {
    uart_putc(uart0, UART_HEADER);
    for (int i = 0; i < length; ++i) {
        uart_putc(uart0, data[i]);
    }
    uart_putc(uart0, UART_FOOTER);
}

/*** THRUSTERS ***/

void thruster_init_oneshot(u8 pin) {
    // initialize the pin
    gpio_init(pin);
    gpio_set_function(pin, GPIO_FUNC_PWM);
    u8 slice = pwm_gpio_to_slice_num(pin);
    u8 channel = pwm_gpio_to_channel(pin);

    // configure PWM
    pwm_set_phase_correct(slice, false);
    pwm_config config = pwm_get_default_config();

    // OneShot125 will run where 1000-2000 map to 125us-250us
    // 96MHz core divided by 12 results in 8MHz, divided by 3999+1 results in 2kHz
    // loop 1000/4000 * 500us = 125us 1500/4000 * 500us = 192us 2000/4000 * 500us
    // = 250us
    pwm_config_set_clkdiv_int(&config, 12);
    pwm_init(slice, &config, true);
    pwm_set_wrap(slice, 3999);
    pwm_set_chan_level(slice, channel, 1500);

    // BLHeli arming sequence not necessary, oneshot takes care of it for us
}

void thruster_output(u8 thruster, u16 level) {
    // level: [1000, 2000]
    if (!assertRange(level, 1000, 2000))
        return;

    u8 slice = pwm_gpio_to_slice_num(thruster_pins[thruster]);
    u8 channel = pwm_gpio_to_channel(thruster_pins[thruster]);

    pwm_set_chan_level(slice, channel, level);
}

void thruster_set_target(u8 thruster, u16 level) {
    thruster_target_pos[thruster] = level;
}

void thruster_set_value(u8 thruster, u16 level) {
    thruster_pos[thruster] = level;
}

void setup_outputs() {
    for (int i = 0; i < NUM_THRUSTERS; ++i) {
        thruster_init_oneshot(thruster_pins[i]);
        thruster_set_target(i, 1500);
        thruster_set_value(i, 1500);
    }

    thruster_prev_loop_us = to_us_since_boot(get_absolute_time());
}

void loop_outputs() {
    u64 now = to_us_since_boot(get_absolute_time());
    u64 elapsed_us = thruster_prev_loop_us - now;
    u16 max_delta = MIN(MAX_DELTA_POS * elapsed_us / 1000000, 0xFFFF);

    // set each output to current value
    for (int i = 0; i < NUM_THRUSTERS; ++i) {
        thruster_output(i, thruster_pos[i]);
    }

    // lerp each output to new value (closer to target)
    for (int i = 0; i < NUM_THRUSTERS; ++i) {
        u16 delta = ABS(thruster_target_pos[i] - thruster_pos[i]);
        i8 sign = ((thruster_target_pos[i] - thruster_pos[i]) > 0) ? 1 : -1;

        if (delta < max_delta) {
            thruster_pos[i] = thruster_target_pos[i];
        } else {
            i16 movement = MIN(delta, max_delta) * sign;
            thruster_pos[i] += movement;
        }
    }
}

int main() {
    bi_decl(bi_program_description("SAS MATE 2023 R&D Firmware V3"));

    set_sys_clock_khz(96000, false);
    setup();

    while (true) {
        loop();
    }

    return 0;
}
