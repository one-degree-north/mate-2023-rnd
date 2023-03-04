// Server side implementation of UDP client-server model
// literally stolen from geek4geeks
//#include <bits/stdc++.h>
#include "udp_comms.h"
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <pthread.h>
<<<<<<< HEAD
#include "esc_software_pwm.h"

#define UDP_PORT     27777
#define MAXLINE  1024
=======
#include <fcntl.h> // Contains file controls like O_RDWR
#include <errno.h> // Error integer and strerror() function
#include <termios.h> // Contains POSIX terminal control definitions
#include "esc_software_pwm.h"

#define UDP_PORT     27777
#define MAXLINE      1024
>>>>>>> 88096d4 (work changes: add udp, other stuff)


// Driver code
void* udp_thread(void* input) {
<<<<<<< HEAD
    // Start serial!
    int serialfd = open("/dev/ttyUSB0");

=======
>>>>>>> 88096d4 (work changes: add udp, other stuff)
    thruster_t* thrusters = (thruster_t*) input;

    int sockfd;
    char buffer[MAXLINE];
    struct sockaddr_in servaddr, cliaddr;

    // Creating socket file descriptor
    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }

    memset(&servaddr, 0, sizeof(servaddr));
    memset(&cliaddr, 0, sizeof(cliaddr));

    // Filling server information
    servaddr.sin_family    = AF_INET; // IPv4
    servaddr.sin_addr.s_addr = INADDR_ANY;
    servaddr.sin_port = htons(UDP_PORT);

    // Bind the socket with the server address
    if ( bind(sockfd, (const struct sockaddr *)&servaddr,
            sizeof(servaddr)) < 0 )
    {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

<<<<<<< HEAD
=======
    int serial_port = setup_serial();

>>>>>>> 88096d4 (work changes: add udp, other stuff)
    for (;;){
        socklen_t len;

        int n;

        len = sizeof(cliaddr);  //len is value/result

        n = recvfrom(sockfd, &buffer, MAXLINE, MSG_WAITALL, ( struct sockaddr *) &cliaddr, &len);

        buffer[n] = '\0';
        printf("Client : %s\n", buffer);

<<<<<<< HEAD
        parse_data(n, buffer, thrusters);
=======
        parse_data(n, buffer, thrusters, serial_port);
>>>>>>> 88096d4 (work changes: add udp, other stuff)
    }

    return 0;
}

<<<<<<< HEAD
void parse_data(int n, char* buf, thruster_t* thrusters) {
    if (n == 0) return; // null byte
    uint8_t cmd = buf[0];
=======
int setup_serial() {
    int serial_port = open("/dev/ttyS3", O_RDWR);
    if (serial_port < 0) {
        printf("Error %i from opening /dev/ttyS3: %s\n", errno, strerror(errno));
    }

    struct termios tty;

    if(tcgetattr(serial_port, &tty) != 0) {
        printf("Error %i from tcgetattr: %s\n", errno, strerror(errno));
    }

    tty.c_cflag &= ~PARENB;
    tty.c_cflag &= ~CSTOPB;
    tty.c_cflag &= ~CSIZE;
    tty.c_cflag |= CS8;
    tty.c_cflag &= ~CRTSCTS;
    tty.c_cflag |= CREAD | CLOCAL;
    tty.c_lflag &= ~ICANON;
    tty.c_lflag &= ~ECHO;
    tty.c_lflag &= ~ECHOE;
    tty.c_lflag &= ~ECHONL;
    tty.c_lflag &= ~ISIG;
    tty.c_iflag &= ~(IXON | IXOFF | IXANY);
    tty.c_iflag &= ~(IGNBRK|BRKINT|PARMRK|ISTRIP|INLCR|IGNCR|ICRNL);
    tty.c_oflag &= ~OPOST;
    tty.c_oflag &= ~ONLCR;
    tty.c_cc[VTIME] = 0;
    tty.c_cc[VMIN] = 0;
    cfsetispeed(&tty, B115200);
    cfsetospeed(&tty, B115200);

    if (tcsetattr(serial_port, TCSANOW, &tty) != 0) {
        printf("Error %i from tcsetattr: %s\n", errno, strerror(errno));
    }

    return serial_port;
}

void parse_data(int n, char* buf, thruster_t* thrusters, int serial_port) {
    if (n == 0) return; // null byte
    uint8_t cmd = buf[0];
    uint8_t msg[6];
    msg[0] = 0xa9;
    msg[5] = 0x9a;

>>>>>>> 88096d4 (work changes: add udp, other stuff)
    switch (cmd) {
        case 0x01:
            uint16_t* ptr = (uint16_t*) (buf + 1);
            for (int i = 0; i < NUM_THRUSTERS; ++i) {
                thrusters[i].target = ptr[i];
            }
            break;
        case 0x02:
            uint8_t servo = *(buf + 1);
<<<<<<< HEAD
            uint16_t value = *(buf + 2);
            break;
        case 0x03:
            uint8_t enable = *(buf + 1);
            break;
    }
}

void send_serial(){

}
=======
            uint16_t value = (*(buf + 3) << 8) + *(buf + 2);

            msg[1] = 0x05;
            msg[2] = servo;
            msg[3] = value >> 8;
            msg[4] = value & 0xFF;
            write(serial_port, msg, sizeof(msg));
            break;
        case 0x03:
            uint8_t enable = *(buf + 1);

            msg[1] = 0x06;
            msg[2] = 0x01;
            msg[3] = 0x00;
            msg[4] = enable;
            write(serial_port, msg, sizeof(msg));
            break;
    }
}
>>>>>>> 88096d4 (work changes: add udp, other stuff)
