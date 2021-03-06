# socket implementation 
# by Robert Reichert 2021
import sys, time
import socket
import struct
import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal

class Client:
    def __init__(self,ipIn='192.168.178.15',portIn=1001):
        self.ip=ipIn            # The server's hostname or IP address
        self.port=portIn        # The port used by the server
    
    def connect(self):
        ## Connect to server (according https://realpython.com/python-sockets/)
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.s.settimeout(1)
            self.s.connect((self.ip, self.port))
        except:
            print('No Server found check IP, Port and Supply')
    def disconnect(self):
        self.s.close()
    def transmission_send(self,command=0,data=0):
        self.s.sendall(struct.pack('<I',(command<<28|data)))
            
    def transmission_receive_single(self):
        self.resive = self.s.recv(4) #recive
        self.in_tup=struct.unpack('<I', self.resive) #convert data to tuple
        return self.in_tup[0]
    def transmission_receive_block(self):
        self.in_buf=np.array([],dtype='int') #create empty input buffer
        #print('wait for data')
        while True:
            #print('.')
            try:
                self.resive = self.s.recv(4) #recive until empty data
                if self.resive==b'':
                    break
                self.in_tup=struct.unpack('<I', self.resive) #convert data to tuple
                
                self.in_buf=np.append(self.in_buf,self.in_tup) #add value
                
                #self.in_buf=np.concatenate((self.in_buf,np.asarray(self.in_tup)),axis=None) #add value to buffer
            except:
                pass
        return self.in_buf

#function to convert a 2s number to int
def TwoSConvert(value): 
    adc_bits=14 # Define number of ADC Bits
    if value<(2**(adc_bits-1)):
        value=value&(0xffff>>(17-adc_bits))
    else:
        value=(value&(0xffff>>(17-adc_bits)))-(2**(adc_bits-1))
    return value

class Receive_block(QObject):
    finished = pyqtSignal()
    getData = pyqtSignal(object)

    def run(self):
        serverClient=Client()
        # connecting to server
        serverClient.connect()

        incommingData=serverClient.transmission_receive_block()
        
        #close server connection
        try:
            serverClient.disconnect()
        except:
            pass
        self.getData.emit(incommingData)
        self.finished.emit()

## testrun
if __name__ == "__main__":
    serverClient=Client('192.168.178.15',1001)
    print ('Received',serverClient.transmission(10, 2, 0, 0))


