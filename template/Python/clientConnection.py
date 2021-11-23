# socket implementation 
# by Robert Reichert 2021

import socket
import struct
import numpy as np

class Client:
    def __init__(self,ipIn='192.168.178.15',portIn=1001):
        self.ip=ipIn            # The server's hostname or IP address
        self.port=portIn        # The port used by the server
    def transmission(self,dat1=0,dat2=0,dat3=0,dat4=0):
        ## Connect to server (according https://realpython.com/python-sockets/)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
            self.s.connect((self.ip, self.port))

        ## Sand data with followring structure --> s.sendall(struct.pack('<I',(command<<28|data))) 
            self.s.sendall(struct.pack('<I',(1<<28|dat1)))
            self.s.sendall(struct.pack('<I',(2<<28|dat2)))
            self.s.sendall(struct.pack('<I',(3<<28|dat3)))
            self.s.sendall(struct.pack('<I',(4<<28|dat4)))
            self.s.sendall(struct.pack('<I',(0)))
            
        ## Resive Data
            self.in_buf=np.array([]) #create empty input buffer
            while True:
                self.resive = self.s.recv(4) #recive until empty data
                if self.resive==b'':
                    break
                self.in_tup=struct.unpack('<I', self.resive) #convert data to tuple
                self.in_buf=np.concatenate((self.in_buf,np.asarray(self.in_tup)),axis=None) #add value to buffer
            return self.in_buf

## testrun
if __name__ == "__main__":
    serverClient=Client('192.168.178.15',1001)
    print ('Received',serverClient.transmission(10, 2, 0, 0))


