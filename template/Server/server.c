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
#include <time.h>

#define PORT 1001
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
    void *gpio, *bram; //pointer to memory data
    uint32_t dat1=0, dat2=0, SampleRate=4, SampleNr=10; //configuraton settings
    int nsmpl; //number of samples
    int stream=0; //set stream (1) or burst (0) mode
    //Measurement time calculation
    int measuring = 0;
    clock_t time_begin;
    double time_spent;

////Load FPGA Programm
    system("cat /usr/src/system_wrapper.bit > /dev/xdevcfg");

////Memory init
    //open memory file
    if((file = open("/dev/mem", O_RDWR)) < 0){
        perror("open");
        return EXIT_FAILURE;
    }
    //map memory to pointer (adress should match Vivado setting)
    bram = mmap(NULL, sysconf(_SC_PAGESIZE), PROT_READ|PROT_WRITE, MAP_SHARED, file, 0x40000000);
    gpio = mmap(NULL, sysconf(_SC_PAGESIZE), PROT_READ|PROT_WRITE, MAP_SHARED, file, 0x42000000);

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
        printf("sock client accepted\n");
        while(1){
            //recive data and breake if connection is closed
            if (recv(sock_client, (char *)&recv_buffer, 4, MSG_DONTWAIT) == 0){
                break;
            }
            //Split incomming data to value and command
            value = recv_buffer & 0xfffffff;
            command = recv_buffer>>28;
            //printf("command: %5d value: %5d \n",command,value);
            switch(command){
                case 0: //reserve
				    break;
                case 1: 
                    dat1=value;
                    break;
                case 2:
                    dat2=value;
				    break;
                case 3:
                    if (value<=16){
				        SampleRate=value;
                    }
				    break;
                case 4:
                    if (value<=10){
				        SampleNr=value;
                    }
				    break;
                case 5:
                    if (value==0||value==1){
                        stream=value;
                    }
				    break;
                case 6:
                    if (value==0||value==1){
                        measuring = value;
                        //Set measurment flag and actual time
				        time_begin = clock();
                        if (value==1){
                            printf("Measurement started\n");
                            *((int32_t *)(gpio+8)) = (0x000b0000);
                            *((int32_t *)(gpio+12)) = (0x80000000);//set tri state register
                            printf("%x\n", (*((uint32_t *)(gpio+4))));
                        }else{
                            printf("Measurement stoped\n");
                            *((int32_t *)(gpio+12)) = (0x00000000);//set tri state register
                            //printf("%x\n", (*((uint32_t *)(gpio+8))));
                        }
                    }
				    break;
                default:
                    printf("Wrong setup data\n");
                    break;
            }

            if(stream==1){
                //Send data every 100ms
                if (measuring == 1 && ((double)(clock() - time_begin)) / CLOCKS_PER_SEC >= (double)SampleRate/1000){
                    double time=((double)(clock() - time_begin)) / CLOCKS_PER_SEC;
                    printf("time: %f mode: %d value: %x\n",time,stream,(*((uint32_t *)(gpio))));
                    time_begin = clock();
                    buffer[0] = (*((uint32_t *)(gpio))); //read GPIO2 input
                    send(sock_client, buffer, 4, MSG_NOSIGNAL);
                }
            }
            else{
                //Check if it is in measuring block mode and has finished (last bit of GPIO2 is trigger)
                if ((measuring == 1 && (*((uint32_t *)(gpio+8)) & 0x80000000) != 0)||(((double)(clock() - time_begin)) / CLOCKS_PER_SEC<1)) { 
                    //while (((double)(clock() - time_begin)) / CLOCKS_PER_SEC<1)
                    time_spent = ((double)(clock() - time_begin)) / CLOCKS_PER_SEC; // measure time
                    printf("time: %f \n",time_spent);
                    *((int32_t *)(gpio+12)) = (0x00000000);//set tri state register
                    for(int j = 0; j < (1<<SampleNr); ++j){
                        buffer[j] = (*((uint32_t *)(bram + 4*j))); //read from bram via IP core "axi_bram_reader"
                    }
                    //Send buffer to client
                    send(sock_client, buffer, 4*(1<<SampleNr), MSG_NOSIGNAL);
                    printf("Measurment ready in %f s\n", time_spent);
                    measuring = 0;
                    break;
                    *((int32_t *)(gpio+12)) = (0x00000000);//set tri state register
                }
            }
            
        }
        close(sock_client);
    }

    close(sock_server);
    return EXIT_SUCCESS;
}

