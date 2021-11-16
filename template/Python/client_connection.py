# socket implementation 
# by Robert Reichert 2021

import socket
import struct
import numpy as np

HOST = '192.168.0.15'  # The server's hostname or IP address
PORT = 1001        # The port used by the server

## Variables to send
dat1=10
dat2=2
dat3=0
dat4=0

## Connect to server (according https://realpython.com/python-sockets/)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

## Sand data with followring structure --> s.sendall(struct.pack('<I',(command<<28|data))) 
    s.sendall(struct.pack('<I',(1<<28|dat1)))
    s.sendall(struct.pack('<I',(2<<28|dat2)))
    s.sendall(struct.pack('<I',(3<<28|dat3)))
    s.sendall(struct.pack('<I',(4<<28|dat4)))
    s.sendall(struct.pack('<I',(0)))
    
## Resive Data
    in_buf=np.array([]) #create empty input buffer
    while True:
        resive = s.recv(4) #recive until empty data
        if resive==b'':
            break
        in_tup=struct.unpack('<I', resive) #convert data to tuple
        in_buf=np.concatenate((in_buf,np.asarray(in_tup)),axis=None) #add value to buffer
    print('Received', in_buf)
