#include <stdio.h>
#include <wiringPi.h>
#include <stdint.h>
#include <stdlib.h>
#include <assert.h>
#include <pthread.h>
#include <time.h>
#include <sys/time.h>
#include "udp_comms.h"
#include "esc_software_pwm.h"

#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))

#define PERIOD_US 4000
#define MAX_DELTA 10    // maximum change per tick (4ms)

thruster_t thrusters[NUM_THRUSTERS];
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
    thrusters[2].pin = 9;
    thrusters[3].pin = 10;
    thrusters[4].pin = 13;
    thrusters[5].pin = 14;
    thrusters[6].pin = 15;
    thrusters[7].pin = 16;

    for (int i = 0; i < NUM_THRUSTERS; i++) {
        pinMode(thrusters[i].pin, OUTPUT);
    }

    // boot cycle
    printf("booting...\n");

    for (int i = 0; i < NUM_THRUSTERS; i++) {
        printf("initial throttle %d\n", i);
        for (int j = 0; j < 400; j++) { // 1000 = 4s
            write_one(i, 1500);
        }

        printf("arming sequence %d\n", i);
        for (int j = 0; j <= 100; j++) { // 100 = 0.4s
            write_one(i, 1400);
        }
        for (int j = 0; j <= 100; j++) { // 100 = 0.4s
            write_one(i, 1500);
        }
        for (int j = 0; j <= 100; j++) { // 100 = 0.4s
            write_one(i, 1400);
        }
    }

    for (int i = 0; i < 1; i++) {
        printf("initial throttle %d\n", i);
        for (int j = 0; j < 1000; j++) { // 1000 = 4s
            write_all(1500);
        }

        printf("arming sequence %d\n", i);
        for (int j = 0; j <= 100; j++) { // 100 = 0.4s
            write_all(1400);
        }

        for (int j = 0; j <= 250; j++) { // 100 = 0.4s
            write_all(1500);
        }

        for (int j = 0; j <= 200; j++) { // 100 = 0.4s
            write_all(1400);
        }
    }

	printf("resetting...\n");
    //write_all(1400);

    for (int i = 0; i < NUM_THRUSTERS; i++) {
        thrusters[i].target = 1400;
        thrusters[i].current = 1400;
    }

    // set up pthreads
    printf("setting up threads...\n");
    struct sched_param param;
    param.sched_priority = 95;
    pthread_create(&update_tid, NULL, udp_thread, thrusters);

    printf("ready!\n");
    printf("format: [id], then [target]\n");
}

void loop() {
    write_cycle(NULL);

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

    if (thrusters[0].enable == 0) exit(0);

}

int main(void) {
    setup();
    for (;;) loop();

	return 0;
}

void* write_cycle(void* input) {
    for (int i = 0; i < NUM_THRUSTERS; ++i) {
        digitalWrite(thrusters[i].pin, HIGH);
        delayMicroseconds(thrusters[i].current);
        digitalWrite(thrusters[i].pin, LOW);
    }

    /*u16 time = 0;
    u16 remaining_time[NUM_THRUSTERS];


    // rising edge
    int start = micros();
    for (int i = 0; i < NUM_THRUSTERS; i++) digitalWrite(thrusters[i].pin, HIGH);
    start = (start + micros()) / 2;

    // copy the array
    for (int i = 0; i < NUM_THRUSTERS; ++i) remaining_time[i] = thrusters[i].current;
    printf("\n");
    // iterate 8 times
    for (int i = 0; i < NUM_THRUSTERS; ++i) {
        // select min
        int min_index = 0;
        for (int j = 1; j < NUM_THRUSTERS; ++j) {
            if (remaining_time[j] < remaining_time[min_index]) min_index = j;
        }
        // sleep that many us
        u16 sleep_time = remaining_time[min_index];
        u16 elapsed_time = (u16) (micros() - start);
        u16 additional_elapsed_time = elapsed_time - time;
        delayMicroseconds(MAX(0, sleep_time - additional_elapsed_time));

        printf("%d %d %d %d |", min_index, time, sleep_time, additional_elapsed_time);

        // set that thruster to low
        digitalWrite(thrusters[min_index].pin, LOW);

        // remove that from others and set it to 0xFFFF
        for (int j = 0; j < NUM_THRUSTERS; ++j) remaining_time[j] -= (sleep_time);
        remaining_time[min_index] = 0xFFFF;
        time += sleep_time;
    }

    delayMicroseconds(PERIOD_US - time);*/
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
        int id;
        int thrust;
        // TODO: make this not dependent on number of %ds
        scanf(" %d", &id);
        scanf(" %d", &thrust);
        fflush(stdin);
        printf("%d, %d\n", id, thrust);
        if (id == 108) {
            for (int i = 0; i < NUM_THRUSTERS; i++) {
                thrusters[i].target = MIN(2000, MAX(1000, thrust % 2048));
            }
        } else if (id != -1){
            thrusters[id % NUM_THRUSTERS].target = MIN(2000, MAX(1000, thrust % 2048));
        } else {
            for (int i = 0; i < NUM_THRUSTERS; i++) {
                thrusters[i].enable = 0;
            }
            return NULL;
        }
        if (thrusters[0].enable == 0) break;
    }
}
