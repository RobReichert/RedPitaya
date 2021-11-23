import sys
from PyQt5 import QtWidgets
import numpy as np
from matplotlib.backends.backend_qtagg import ( FigureCanvas, NavigationToolbar2QT as NavigationToolbar)


##Include clases from other files
from templateUI import Ui_MainWindow
from clientConnection import Client

#define button press function
def ButtonPressSend():
    #Get data from UI
    data1=ui.inputData1.text()
    data2=ui.inputData2.text()
    data3=ui.inputData3.text()
    data4=ui.inputData4.text()
    print(data1)
    print(data2)
    print(data3)
    print(data4)
    
    #Get data from server
    serverClient=Client('192.168.178.15',1001)
    incommingData=serverClient.transmission(int(data1), int(data2), int(data3), int(data4))
    print ('Received',incommingData)
    
    #update diagram data
    ui.line.set_data(np.linspace(0, 10, incommingData.size), incommingData)
    
    #Rescale and redraw diagram
    ui.ax.relim()
    ui.ax.autoscale_view()
    ui.line.figure.canvas.draw()
    

#Open QT Window and import as ui
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()

#connect button press function
ui.buttonSend.clicked.connect(ButtonPressSend)

#insert matplotlib graph
layout = QtWidgets.QVBoxLayout(ui.MplWidget)
canvas = FigureCanvas()
layout.addWidget(canvas)
layout.addWidget(NavigationToolbar(canvas,ui.MplWidget))
ui.ax = canvas.figure.subplots()
t = np.linspace(0, 10, 101)
ui.line, = ui.ax.plot(0, 0,label='linie1')
ui.ax.set_title("Test Chart")
ui.ax.grid(True)             
ui.ax.legend()

sys.exit(app.exec_())