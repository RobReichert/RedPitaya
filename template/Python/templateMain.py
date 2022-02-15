import sys
import numpy as np
#import time
from matplotlib.backends.backend_qtagg import ( FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import matplotlib.figure as mpl_fig
import matplotlib.animation as anim

import typing 


##Include clases from other files
from templateUI import Ui_MainWindow, QtWidgets
from clientConnection import Client

#function to convert a 2s number to int
def TwoSConvert(value): 
    adc_bits=14 # Define number of ADC Bits
    if value<(2**(adc_bits-1)):
        value=value&(0xffff>>(17-adc_bits))
    else:
        value=(value&(0xffff>>(17-adc_bits)))-(2**(adc_bits-1))
    return value
    
class Window(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        # setup ui
        QtWidgets.QWidget.__init__(self,parent=None)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # connect button press function
        self.ui.buttonSend.clicked.connect(self.ButtonPressSend)
        self.ui.buttonMeasurement.clicked.connect(self.ButtonPressMeasure)
        self.ui.radioButtonStram.toggled.connect(self.RadioButtonMode)
        # insert matplotlib graph
        self.layout = QtWidgets.QVBoxLayout(self.ui.MplWidget)
        self.canvas = MyFigureCanvas(x_len=1000, y_range=[-8192, 8192], interval=1)
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(NavigationToolbar(self.canvas,self.ui.MplWidget))
        # init variables
        self.measurement=0
        self.mode=0

    def closeEvent(self, event):
        self.canvas.close() # stop animation
        #close server connection
        try:
            serverClient.disconnect()
        except:
            pass
        
    ## Define button press function
    def ButtonPressSend(self):
        #Send data from UI
        serverClient.connect()
        serverClient.transmission_send(1,int(self.ui.inputData1.text())) # Send data1 to server
        serverClient.transmission_send(2,int(self.ui.inputData2.text())) # Send data2 to server
        serverClient.transmission_send(3,int(self.ui.inputData3.text())) # Send Sample Rate to server
        serverClient.transmission_send(4,int(self.ui.inputData4.text())) # Send Sample Nr. to server
         
    def ButtonPressMeasure(self):
        # connecting to server
        serverClient.connect()
        
        ## change mesuring mode
        # measuring
        if self.measurement==0: 
            # general stuff
            self.ui.buttonMeasurement.setText("Stop Measurement") # change button text
            self.measurement=1
            serverClient.transmission_send(6,1) # Send measure to server
            print("Measurement startet")
            # streaming mode settings
            if self.ui.radioButtonStram.isChecked():
                self.canvas.animate()
                print('stream')
            # block mode settings
            else:
                self.canvas.update_canvas()
        # stop
        else: 
            # general stuff
            self.ui.buttonMeasurement.setText("Start Measurement") # change button text
            self.measurement=0
            serverClient.transmission_send(6,0) # Send stop to server
            print("Measurement stopped")
            # streaming mode settings
            if self.ui.radioButtonStram.isChecked():
                self.canvas.close() # stop animation
                #close server connection
                try:
                    serverClient.disconnect()
                except:
                    pass
            # block mode settings
            else:
                pass
        
    def RadioButtonMode(self):
        # stop measurement
        if self.measurement==1: 
            self.ButtonPressMeasure()
        # connecting to server
        serverClient.connect()
        
        if self.ui.radioButtonStram.isChecked():
            # change text to Streaming mode version
            self.ui.labelData3.setText("Sample Rate [ms]")
            self.ui.inputData3.setText("10")
            # send initial data for streaming mode
            serverClient.transmission_send(5,1) # Send streaming mode to server
            serverClient.transmission_send(3,int(self.ui.inputData3.text())) # Send Sample Rate to server
        else:
            # change text to Block mode version
            self.ui.labelData3.setText("Sample Rate [125MHz/2^x]")
            self.ui.inputData3.setText("7")
            # send initial data for block mode
            serverClient.transmission_send(5,0) # Send block mode to server
            serverClient.transmission_send(3,int(self.ui.inputData3.text())) # Send Sample Rate to server
   
## This is the FigureCanvas in which the plot is drawn. (according https://stackoverflow.com/questions/57891219/how-to-make-a-fast-matplotlib-live-plot-in-a-pyqt5-gui)
class MyFigureCanvas(FigureCanvas, anim.FuncAnimation):
    def __init__(self, x_len:int, y_range:typing.List, interval:int) -> None:
        # x_len:       The nr of data points shown in one plot.
        # y_range:     Range on y-axis.
        # interval:    Get a new datapoint every .. milliseconds.
        FigureCanvas.__init__(self, mpl_fig.Figure())
        
        # Range settings
        self.x_len = x_len
        self.y_range = y_range

        # Store lists x,y and y2
        self.x = list(range(0, x_len))
        self.y = [0] * x_len
        self.y2 = [0] * x_len
        # Store interval
        self.interval=interval
        # Store a figure and ax
        self.ax  = self.figure.subplots()
        self.ax.set_ylim(ymin=self.y_range[0], ymax=self.y_range[1])
        self.line, = self.ax.plot(self.x, self.y,label='Channel1')
        self.line2, = self.ax.plot(self.x, self.y2,label='Channel2')
        
        # Set polt options
        self.ax.set_title("Test Chart")
        self.ax.grid(True)             
        self.ax.legend()
                
    def animate(self):
        # update canvas data
        try:
            self.scale1=float(MainWindow.ui.inputScal1.text())
            self.scale2=float(MainWindow.ui.inputScal2.text())
            self.ymax=float(MainWindow.ui.inputRangeMax.text())
            self.ymin=float(MainWindow.ui.inputRangeMin.text())
        except:
            self.scale1=0
            self.scale2=0
            self.ymax=1
            self.ymin=-1
            print('use a number with decimal dot')
        self.ax.set_ylim(ymin=self.ymin, ymax=self.ymax) 
        
        # Call superclass constructors
        anim.FuncAnimation.__init__(self, self.figure, self.update_canvas_stream, fargs=([self.y,self.y2]), interval=self.interval, blit=True)
        # Redraw figure and legend
        self.figure.canvas.draw()
                
    def close(self):    
        anim.FuncAnimation.pause(self)
                
    def update_canvas_stream(self, i, y, y2) -> None:
        # This function gets called regularly by the timer.
        #serverClient=Client()
        try:
            incommingData=serverClient.transmission_receive_single()
            high=incommingData>>16
            low=incommingData&0x0000ffff
        except:
            high=0
            low=0
        
        y.append(int(TwoSConvert(high))*self.scale1)     # Add new datapoint
        y = y[-self.x_len:]                        # Truncate list _y_
        
        y2.append(int(TwoSConvert(low))*self.scale2)     # Add new datapoint
        y2 = y2[-self.x_len:]                        # Truncate list _y_
        
        self.line.set_ydata(y)
        self.line2.set_ydata(y2)
        return self.line, self.line2
    
    def update_canvas(self):
        incommingData=serverClient.transmission_receive_block()
        self.line.set_data(np.linspace(0, int(self.ui.inputData4.text()), incommingData.size), incommingData)

if __name__ == "__main__":
    #initialize variable
    
    #Open QT Window and import as ui
    app=QtWidgets.QApplication(sys.argv)
    MainWindow=Window()
    MainWindow.setGeometry(300, 300, 800, 600) #X co-ordinate, Y co-ordinate, Width, Height
    MainWindow.show()
    
    #crate client
    serverClient=Client()
    
    
    
    
    
    












