#include <stdio.h>
#include <wiringPi.h>
#include <stdint.h>
#include <stdlib.h>
#include <assert.h>
#include <pthread.h>
#include "esc_software_pwm.h"

#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))

#define u8 uint8_t
#define u16 uint16_t

#define NUM_THRUSTERS 2

#define PERIOD_US 4000
#define MAX_DELTA 8    // maximum change per tick (4ms)

typedef struct Thruster {
    u8 enable;      // 0 if disabled
    u8 pin;         // board pin according to wiringPi
    u16 target;     // target pulse in us (1000-1800)
    u16 current;    // current pulse in us (1000-1800)
} thruster_t;

thruster_t thrusters[NUM_THRUSTERS];
pthread_t tids[NUM_THRUSTERS];
pthread_t update_tid;

void setup() {
    // set up pins and peripherals
    printf("setting up pins & peripherals...\n");
    printf("running with %d thrusters\n", NUM_THRUSTERS);

    wiringPiSetup();

    // set up default values
    for (int i = 0; i < NUM_THRUSTERS; i++) {
        thrusters[i].enable = 1;
        thrusters[i].target = 1500;
        thrusters[i].current = 1500;
    }
    thrusters[0].pin = 4;
    thrusters[1].pin = 6;
    /*thrusters[2].pin = 9;
    thrusters[3].pin = 10;
    thrusters[4].pin = 13;
    thrusters[5].pin = 14;
    thrusters[6].pin = 15;
    thrusters[7].pin = 16;*/

    for (int i = 0; i < NUM_THRUSTERS; i++) {
        pinMode(thrusters[i].pin, OUTPUT);
    }

    // boot cycle
    printf("booting...\n");
    struct sched_param param;
    param.sched_priority = 95;

    for (int i = 0; i < NUM_THRUSTERS; i++) {
        printf("initial throttle %d\n", i);
        for (int j = 0; j < 500; j++) { // 1000 = 4s
            write_one(i, 1500);
        }

        printf("arming sequence %d\n", i);
        for (int j = 0; j <= 100; j++) { // 100 = 0.4s
            write_one(i, 1400);
        }
        for (int j = 0; j <= 250; j++) { // 100 = 0.4s
            write_one(i, 1500);
        }
        for (int j = 0; j <= 250; j++) { // 100 = 0.4s
            write_one(i, 1400);
        }

        pthread_create(&(tids[i]), NULL, write_cycle, &(thrusters[i]));
        pthread_setschedparam(tids[i], SCHED_FIFO, &param);
    }

	printf("resetting...\n");
    //write_all(1400);

    for (int i = 0; i < NUM_THRUSTERS; i++) {
        thrusters[i].target = 1400;
        thrusters[i].current = 1400;
    }

    // set up pthreads
    printf("setting up threads...\n");
    pthread_create(&update_tid, NULL, update_cycle, "update");

    printf("ready!\n");
    printf("format: ![id]->[target]\n");
}

void loop() {
    int id;
    int thrust;
    // TODO: make this not dependent on number of %ds
    scanf(" %d", &id);
    scanf(" %d", &thrust);
    fflush(stdin);
    printf("%d, %d\n", id, thrust);
    if (id != -1){
        thrusters[id % NUM_THRUSTERS].target = MIN(2000, MAX(1000, thrust % 2048));
    } else if (id == 108) {
        for (int i = 0; i < NUM_THRUSTERS; i++) {
            thrusters[i].target = MIN(2000, MAX(1000, thrust % 2048));
        }
    } else {
        for (int i = 0; i < NUM_THRUSTERS; i++) {
            thrusters[i].enable = 0;
            pthread_join(tids[i], NULL);
        }
        pthread_join(update_tid, NULL);
        exit(0);
    }

    delayMicroseconds(PERIOD_US);
}

int main (void) {
    setup();
    for (;;) loop();

	return 0;
}

void* write_cycle(void* input) {
    thruster_t* thruster = (thruster_t*) input;

    for (;;) {
        digitalWrite(thruster->pin, HIGH);
        delayMicroseconds(thruster->current);
        digitalWrite(thruster->pin, LOW);
        delayMicroseconds(PERIOD_US - thruster->current);

        if (thruster->enable == 0) break;
    }
}

void write_one(uint8_t i, uint16_t ms_on) {
	if (ms_on < 1000 || ms_on > 2000) return;

    digitalWrite(thrusters[i].pin, HIGH);
	delayMicroseconds(ms_on);
	digitalWrite(thrusters[i].pin, LOW);
	delayMicroseconds(PERIOD_US - ms_on);
}

void write_all(uint16_t ms_on) {
	if (ms_on < 1000 || ms_on > 2000) return;

    for (int i = 0; i < NUM_THRUSTERS; i++) digitalWrite(thrusters[i].pin, HIGH);
	delayMicroseconds(ms_on);
	for (int i = 0; i < NUM_THRUSTERS; i++) digitalWrite(thrusters[i].pin, LOW);
	delayMicroseconds(PERIOD_US - ms_on);
}

void* update_cycle(void* input) {
    for (;;) {
        // update current thruster values
        for (int i = 0; i < NUM_THRUSTERS; i++) {
            if (thrusters[i].current < thrusters[i].target) {
                thrusters[i].current = MIN(thrusters[i].target, thrusters[i].current + MAX_DELTA);
            } else if (thrusters[i].current > thrusters[i].target) {
                thrusters[i].current = MAX(thrusters[i].target, thrusters[i].current - MAX_DELTA);
            }
        }

        // print thruster positions
        for (int i = 0; i < NUM_THRUSTERS; i++) {
            //printf("[K[%d]: %d -> %d\n", thrusters[i].pin, thrusters[i].current, thrusters[i].target);
        }

        delayMicroseconds(PERIOD_US);

        if (thrusters[0].enable == 0) break;
    }
}
