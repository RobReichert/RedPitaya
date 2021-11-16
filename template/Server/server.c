/*Server vor Ethernet connection to RedPiraya

by Robert Reichert 2021
Modified from Pavel Demin's server.c
*/

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <math.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 1001
#define NR_SAMPLE 12 //number of samples
#define READBUFFER_SICE 8192 //maximum sice for readbuffer

int main(){
    //Template Variables
    int file; //file descriptor for memoryfile
    int sock_server; //Socket for Server
    int sock_client; //Client identefire 
    struct sockaddr_in addr; //Server address struct
    int optval=1; //Number of socket options
    uint32_t recv_buffer; //Buffer for reciving data from client
    uint32_t recv_buffer_old;
    uint32_t value;//Incomming value
    uint32_t command;//Incomming command number
    uint32_t buffer[READBUFFER_SICE];//buffer for data transmission 
    //Application dependend Variables
    void *cfg, *dat; //pointer to memory data
    uint32_t dat1=0, dat2=0, dat3=0, dat4=0;
    int nsmpl//number of samples
    //Measurement time calculation
    int measuring = 0;
    clock_t time_begin;
    double time_spent;

////Load FPGA Programm
    //system("cat /usr/src/Programm.bit > /dev/xdevcfg");

////Memory init
    //open memory file
    if((file = open("/dev/mem", O_RDWR)) < 0){
        perror("open");
        return EXIT_FAILURE;
    }
    //map memory to pointer (adress should match Vivado setting)
    dat = mmap(NULL, sysconf(_SC_PAGESIZE), PROT_READ|PROT_WRITE, MAP_SHARED, file, 0x40000000);
    cfg = mmap(NULL, sysconf(_SC_PAGESIZE), PROT_READ|PROT_WRITE, MAP_SHARED, file, 0x42000000);

////Server init
    //create socket for Server
    if((sock_server = socket(AF_INET, SOCK_STREAM, 0)) < 0){
        perror("socket");
        return EXIT_FAILURE;
    }
    //set socket options
    setsockopt(sock_server, SOL_SOCKET, SO_REUSEADDR, (void *)&optval , sizeof(optval));
    //setup listening address
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(PORT);
    //bind adress to socket
    if(bind(sock_server, (struct sockaddr *)&addr, sizeof(addr)) < 0){
        perror("bind");
        return EXIT_FAILURE;
    }
    //listening for incoming connections
    listen(sock_server, 1024);
    printf("Listening on port %i ...\n", PORT);
    
////Client connection    
    while(1){
        //Wait for client connection request
        if((sock_client = accept(sock_server, NULL, NULL)) < 0){
            perror("accept");
            return EXIT_FAILURE;
        }
        while(1){
            //recive data and breake if connection is closed
            if (recv(sock_client, (char *)&recv_buffer, 4, MSG_DONTWAIT) == 0){
                break;
            }
            //Split incomming data to value and command
            value = recv_buffer & 0xfffffff;
            command = recv_buffer>>28
            switch(command){
                case 0: //Write config to Memory
				    *((int32_t *)(cfg)) = (dat1) + (dat2<<8) + (dat3<<16) + (dat4<<24);
                    //Set measurment flag and actual time
				    time_begin = clock();
				    measuring = 1;
				    break;
                case 1:
                    dat1 = recv_buffer & 0xff;
                    break;
                case 2:
                    dat2 = recv_buffer & 0xff;
				    break;
                case 3:
				    dat3 = recv_buffer & 0xff;
				    break;
                case 4:
				    dat4 = recv_buffer & 0xff;
				    break;
                default:
                    printf("Wrong setup data\n");
                    break;
            }

            //Check if it is in measuring mode and has finished (first bit od GPIO2 is trigger)
            if (measuring == 1 && (*((uint32_t *)(cfg + 8)) & 1) != 0) { 
      	        time_spent = ((double)(clock() - time_begin)) / CLOCKS_PER_SEC; // measure time
                //Read data 
                /*  example for single data
                    buffer = (*((uint32_t *)(cfg + 8))); //read GPIO2 input
                    send(sock_client, buffer, sizeof(buffer), MSG_NOSIGNAL);
                */
      	        for(j = 0; j < NR_SAMPLE; ++j){
                    buffer[j] = (*((uint32_t *)(dat + 4*j))); //read from bram via IP core "axi_bram_reader"
                }
			    //Send buffer to client
      	        send(sock_client, buffer, 4*NR_SAMPLE, MSG_NOSIGNAL);
      	        printf("Measurment ready in %f s\n", time_spent);
		        measuring = 0;
		        break;
            }

        }
        close(sock_client);
    }

    close(sock_server);
    return EXIT_SUCCESS;
}