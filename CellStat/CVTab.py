# CVTab.py
from multiprocessing import Process
from operator import index
from socket import CAPI
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import serial
from datetime import datetime

from ping import *
from cailbration import *



BAUD_RATE = 115200
TIMEOUT = 3

class CVTab(QWidget):
    def __init__(self, port):
        super().__init__()
        self.process_flag = False
        self.layout = QGridLayout()
        self.serial_connection = None
        
        # Label and Line Edit for CV Tab
        i = QLabel("CV Tab")
        self.PortNum= port
        

      # Cyclic Voltammetry (CV) parameters
      # L = Label 
      # I = Input
        self.L_NumCycles = QLabel("Number of Cycles:")
        self.I_NumCycles = QLineEdit()
        self.I_NumCycles.setPlaceholderText("Enter the number of cycles")

        self.L_StartVoltage = QLabel("Start Potential (V):")
        self.I_StartVoltage = QLineEdit()
        self.I_StartVoltage.setPlaceholderText("Enter the start potential between -2.5 and +2.5 V")

        self.L_FirstVoltage = QLabel("First Inversion Potential (V):")
        self.I_FirstVoltage = QLineEdit()
        self.I_FirstVoltage.setPlaceholderText("Enter the first inversion potential")

        self.L_SecondVoltage = QLabel("Second Inversion Potential (V):")
        self.I_SecondVoltage = QLineEdit()
        self.I_SecondVoltage.setPlaceholderText("Enter the second inversion potential")

        self.L_ScanRate = QLabel("Scan Rate (V/s):")
        self.I_ScanRate = QLineEdit()
        self.I_ScanRate.setPlaceholderText("Enter the scan rate")


        #added radio buttons for the resistor and capcitor
        self.L_CurrentRange = QLabel("Enter the i range :")  # Create QLabel
        self.RangeGroup = QButtonGroup()
        self.RangeList = QHBoxLayout()

        for i in CurrentRange:# taken from the cailbarion file
            Btn = QRadioButton(i)
            self.RangeGroup.addButton(Btn)
            self.RangeList .addWidget(Btn)

        #again for the capcitor filter
        self.L_CapRange = QLabel(" Enter the Cap value in F :")  # Create QLabel
        self.CapGroup = QButtonGroup()
        self.CapList = QHBoxLayout()


        for i in CapacitorLabels :# taken from the cailbarion file
            Btn = QRadioButton(i)
            self.CapGroup.addButton(Btn)
            self.CapList.addWidget(Btn)

        self.L_FileName = QLabel("File Name:")
        self.I_FileName = QLineEdit()
        self.I_FileName.setPlaceholderText("Enter a name for the CSV file")
        
        
        # Start and Stop and Save Buttons 
        self.StartButton = QPushButton("Start")
        self.StartButton.clicked.connect(self.Run_CMD)
        self.StopButton = QPushButton("Stop")
        self.StopButton.clicked.connect(self.Stop_CMD)
        self.SaveButton = QPushButton("Save")
        #self.SaveButton.clicked.connect(self.Save)

        self.layout.addWidget(self.L_FileName,0,0)
        self.layout.addWidget(self.I_FileName,0,1)
        self.layout.addWidget(self.L_StartVoltage,1,0)
        self.layout.addWidget(self.I_StartVoltage,1,1)
        self.layout.addWidget(self.L_FirstVoltage,2,0)
        self.layout.addWidget(self.I_FirstVoltage,2,1)
        self.layout.addWidget(self.L_SecondVoltage,3,0)
        self.layout.addWidget(self.I_SecondVoltage,3,1)
        
        self.layout.addWidget(self.L_NumCycles,0,2)
        self.layout.addWidget(self.I_NumCycles,0,3)
        self.layout.addWidget(self.L_ScanRate,1,2)
        self.layout.addWidget(self.I_ScanRate,1,3)
        self.layout.addWidget(self.L_CurrentRange,2,2)
        self.layout.addLayout(self.RangeList,2,3)
        self.layout.addWidget(self.L_CapRange,3,2)
        self.layout.addLayout(self.CapList,3,3)

        self.layout.addWidget(self.StopButton,4,0)
        self.layout.addWidget(self.StartButton,4,1,1,1)
        self.layout.addWidget(self.SaveButton,4,3)
       
       # Creating the canvas for plotting and the toolbar
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot(111)
       
        self.layout.addWidget(self.toolbar,6,0,1,2)
        self.layout.addWidget(self.canvas,7,0,5,5)
        self.setLayout(self.layout)

    def update_port(self, newport):
        self.PortNum = newport

        # Update any other components or processes that depend on the port

    def is_process_running(self):
        return self.process_flag is True and self.process.is_alive()

    # Function to run the CV process and to check the inputs
    def Run_CMD(self):
        try:
          
            #check if the input is empty
            if self.I_NumCycles.text()=='' or self.I_StartVoltage.text()=='' or self.I_FirstVoltage.text()=='' or self.I_SecondVoltage.text()=='' or self.I_ScanRate.text()=='' or self.I_FileName.text()=='':
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Please fill in all the fields.")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
            #check if buttons are selected
            i= [i for i, radio_btn in enumerate(self.RangeGroup.buttons()) if radio_btn.isChecked()]
            k= [k for k, radio_btn in enumerate(self.CapGroup.buttons()) if radio_btn.isChecked()]
            self.Rindex=i[0]
            self.Cindex=k[0]
            if not i[0]:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Please select a current range.")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                
            
            if not k[0]:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Please select a capacitor range.")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                
            
        
            self.cycnum =        int(self.I_NumCycles.text())
            self.startvolt =     float(self.I_StartVoltage.text())
            self.firstvolt =     float(self.I_FirstVoltage.text())
            self.secondvolt =    float(self.I_SecondVoltage.text())
            self.scanrate =      float(self.I_ScanRate.text())
            self.resistorval =   int(ResistorValues[self.Rindex]) 
            self.CAPVal =        int(CapacitorValues[self.Cindex])
            self.filename =      self.I_FileName.text()

            #check to see if the cycle is in the correct range
            if self.cycnum <= 0 or self.cycnum > 100:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Number of cycles must be between 1 and 100")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return
            #check to see if the voltage is in the correct range
            if self.startvolt < -2.5 or self.startvolt > 2.5 or self.firstvolt < -2.5 or self.firstvolt > 2.5 or self.secondvolt < -2.5 or self.secondvolt > 2.5:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Start potential must be between -2.5 and +2.5 V")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return
            #check to see if the scan rate is in the correct range
            if self.scanrate <= 0.00001 or self.scanrate > 60:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Scan rate must be between 0.00001 and 60 V/s")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
            
                return
            

            DAC1= int(round (self.startvolt /(DAC_QUANT * GAIN)+DAC_OFFSET))
            DAC2= int(round (self.firstvolt /(DAC_QUANT * GAIN)+DAC_OFFSET))
            DAC3= int(round (self.secondvolt /(DAC_QUANT * GAIN)+DAC_OFFSET))

            numpoint= abs(DAC2-DAC1) + abs(DAC3-DAC2) + abs(DAC1-DAC3)
            self.totpoint= numpoint * self.cycnum
            #check to see is the there is enough points
            if self.totpoint > 52000:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("total number of points is too large")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                
        except:
            return
        
        
        print("Running CV with the following parameters:")
        print(f"Number of cycles: {self.cycnum}")
        print(f"Start potential: {self.startvolt}")
        print(f"First inversion potential: {self.firstvolt}")
        print(f"Second inversion potential: {self.secondvolt}")
        print(f"Scan rate: {self.scanrate}")
        print(f"Resistor value: {self.resistorval}")
        print(f"Capacitor value: {self.CAPVal}")
        print(f"Filename: {self.filename}")


     
        
        # Only start if there's no active process
        if self.process_flag is False or not self.process.is_alive():
            self.process = Process(target=self.execute_CV, args=(self,))
            self.process.start()

    def Stop_CMD(self):
        # Terminate the process if it's running
        if self.process is not None and self.process.is_alive():
            self.process.terminate()
            self.process.join()  # Ensure the process has fully terminated
            if self.serial_connection is not None:
                self.serial_connection.close()
                self.serial_connection.close()
            print("Task terminated")


    def Save(self):
        # Save graph as a png file
        self.figure.savefig(self.filename + ".png")
        print("Graph saved as " + self.filename + ".png")


    def execute_CV(self):


        CMDid= 1 #this is to show what kind of  test is being done to the teensy   
        period = int(round(1e6 / (self.scanrate * DAC_QUANT)))
        DAC1= int(round (self.startvolt /(DAC_QUANT * GAIN)+DAC_OFFSET))
        DAC2= int(round (self.firstvolt /(DAC_QUANT * GAIN)+DAC_OFFSET))
        DAC3= int(round (self.secondvolt /(DAC_QUANT * GAIN)+DAC_OFFSET))

    
        # Transmit the CV parameters to the Teensy
        #transmit= id, period, DAC1, DAC2, DAC3, cycles, DAC_OFFSET
        transmit = str(CMDid)  + "," + str( period) + "," + str(DAC1) + "," + str(DAC2) + "," + str(DAC3) + "," + str(self.cycnum) + "," + str(DAC_OFFSET) +"\n"

        portname = "COM" + self.PortNum
        serial_connection = serial.Serial(portname, BAUD_RATE, TIMEOUT)

        message = transmit.encode("utf-8")
        serial_connection.write(message)
        print("You Transmitted:", transmit)

        # Get the current date and time
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")


        # Send CV parameters to Teensy to start measurement
        numpoint= int(abs(DAC2-DAC1) + abs(DAC3-DAC2) + abs(DAC1-DAC3))
        self.totpoint
        
        dataamount= 0
        Data = np.zeros((numpoint, self.cycnum + 1))
        # Loop to detect end of measurement message from Arduino
        while True:
            received = serial_connection.readline()[:-2]
            received_utf8 = received.decode("utf-8")
            if received_utf8 == "END":
                print("Measurement completed")
                break
            if received_utf8 != "" and received_utf8 != "END":
                
                for k in range(1, self.cycnum + 1):
                    for j in range(numpoint):
                        data = serial_connection.readline()[:-2]
                        data_utf8 = data.decode("utf-8")
                        line = data_utf8.split(",")
                        Data[j, 0] = (int(line[0]) - DAC_OFFSET) * GAIN * DAC_QUANT
                        Data[j, k] =(int(line[1]) - ADC_OFFSET[int(self.Rindex)]) * ADC_QUANT[int(self.Rindex)] * CONV_COEFF * (CurrentMultiplier[self.Rindex]/ResistorValues[self.Rindex]) 
                        print(Data[j, 0], Data[j, k])
                        dataamount += 1
                        if dataamount <= self.totpoint:
                            print("error too many data points")
                            break
            
        
        # Plot the data
        
        self.ax.clear()
        for k in range(1, self.cycnum + 1):
                Data[:, k] *= CurrentMultiplier[self.Rindex]
                self.ax.plot(Data[:, 0], Data[:, k], label="Cycle " + str(k))
        self.ax.grid(True)
        self.ax.legend()
        self.ax.set_xlabel('Voltage (V)')
        self.ax.set_ylabel('Current (' + CurrentUnit[self.Rindex] + ')')
        self.ax.set_title('Cyclic Voltammetry')
        self.canvas.draw()

        serial_connection.close()

        #get date when the data was taken
        
       
        
        # Save the data to a CSV file adding the date and time
        if self.filename == 
        with open(self.filename + ".csv", "w") as file:
            file.write("Data taken on: " + dt_string + "\n")
            file.write("Voltage (V),Current (" + CurrentUnit[self.Rindex] + ")\n")
            for k in range(1, self.cycnum + 1):
                for j in range(numpoint):
                    file.write(f"{Data[j, 0]},{Data[j, k]}\n")
        print("Data saved to " + self.filename + ".csv")



        print("Plotting completed")
