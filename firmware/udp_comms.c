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
#include "esc_software_pwm.h"

#define UDP_PORT     27777
#define MAXLINE  1024


// Driver code
void* udp_thread(void* input) {
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

    for (;;){
        socklen_t len;

        int n;

        len = sizeof(cliaddr);  //len is value/result

        n = recvfrom(sockfd, &buffer, MAXLINE, MSG_WAITALL, ( struct sockaddr *) &cliaddr, &len);

        buffer[n] = '\0';
        printf("Client : %s\n", buffer);

        parse_data(n, buffer, thrusters);
    }

    return 0;
}

void parse_data(int n, char* buf, thruster_t* thrusters) {
    if (n == 0) return; // null byte
    uint8_t cmd = buf[0];
    switch (cmd) {
        case 0x01:
            uint16_t* ptr = (uint16_t*) (buf + 1);
            for (int i = 0; i < NUM_THRUSTERS; ++i) {
                thrusters[i].target = ptr[i];
            }
            break;
        case 0x02:
            uint8_t servo = *(buf + 1);
            uint16_t value = *(buf + 2);
            break;
        case 0x03:
            uint8_t enable = *(buf + 1);
            break;
    }
}
