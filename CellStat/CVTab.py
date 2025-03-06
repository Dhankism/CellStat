# CVTab.py
import multiprocessing
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
import time

from ping import *
from cailbration import *

BAUD_RATE = 115200
TIMEOUT = 30
ResetCMD="RESET\n"

class CVWorker(QThread):
    data_ready = pyqtSignal(np.ndarray)

    def __init__(self, transmit, port_name):
        super().__init__()
        self.transmit = transmit
        self.port_name = port_name

    def run(self):
        try:
            # Open the serial connection
            print(str(self.port_name))
            self.serial_connection = serial.Serial(self.port_name, BAUD_RATE, timeout=TIMEOUT)

            # Send the message to the Teensy
            message = self.transmit.encode("utf-8")
            self.serial_connection.write(message)
            print("You Transmitted:", self.transmit)

            dataamount = 0
            Data = []
            buffer = ""
            start_time = time.time()
            time.sleep(10)
            # Loop to detect end of measurement message from Arduino
            while True:
                while (self.serial_connection.in_waiting == 0 and (time.time() - start_time) > 40):
                    pass
                
                received = self.serial_connection.readline().decode("utf-8")
                buffer += received
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line == "END":
                        print("Measurement completed")
                        self.serial_connection.close()
                        Data = np.array(Data)
                        self.data_ready.emit(Data)
                        return
                    if line:
                        print(line)
                        line = line.split(",")
                        try:
                            voltage = (int(line[0]) - DAC_OFFSET) * GAIN / DAC_QUANT
                            current = (int(line[1]) - ADC_OFFSET[2]) * ADC_QUANT  * CurrentMultiplier[2] / ResistorValues[2]
                            print(voltage, ",", current)
                            Data.append([voltage, current])
                            dataamount += 1
                        except ValueError as e:
                            print(f"ValueError: {e}")
                            continue
        except Exception as e:
            print(f"Exception in CVWorker: {e}")
        finally:
            if self.serial_connection.is_open:
                self.serial_connection.write(ResetCMD.encode("utf-8"))
                self.serial_connection.close()

class CVTab(QWidget):
    def __init__(self, port):
        super().__init__()
        self.layout = QGridLayout()
        self.serial_connection = None
        
        # Label and Line Edit for CV Tab
        i = QLabel("CV Tab")
        self.PortNum = port
        self.worker = None
        self.processFlag= False

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

        # Added radio buttons for the resistor and capacitor
        self.L_CurrentRange = QLabel("Enter the i range :")
        self.RangeGroup = QButtonGroup()
        self.RangeList = QHBoxLayout()

        for i in CurrentRange:# taken from the cailbarion file
            Btn = QRadioButton(i)
            self.RangeGroup.addButton(Btn)
            self.RangeList.addWidget(Btn)

        self.L_CapRange = QLabel("Enter the Cap value in F :")
        self.CapGroup = QButtonGroup()
        self.CapList = QHBoxLayout()

        for i in CapacitorLabels:
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


        self.layout.addWidget(self.L_FileName, 0, 0)
        self.layout.addWidget(self.I_FileName, 0, 1)
        self.layout.addWidget(self.L_StartVoltage, 1, 0)
        self.layout.addWidget(self.I_StartVoltage, 1, 1)
        self.layout.addWidget(self.L_FirstVoltage, 2, 0)
        self.layout.addWidget(self.I_FirstVoltage, 2, 1)
        self.layout.addWidget(self.L_SecondVoltage, 3, 0)
        self.layout.addWidget(self.I_SecondVoltage, 3, 1)
        self.layout.addWidget(self.L_NumCycles, 0, 2)
        self.layout.addWidget(self.I_NumCycles, 0, 3)
        self.layout.addWidget(self.L_ScanRate, 1, 2)
        self.layout.addWidget(self.I_ScanRate, 1, 3)
        self.layout.addWidget(self.L_CurrentRange, 2, 2)
        self.layout.addLayout(self.RangeList, 2, 3)
        self.layout.addWidget(self.L_CapRange, 3, 2)
        self.layout.addLayout(self.CapList, 3, 3)
        self.layout.addWidget(self.StartButton, 4, 0, 1, 3)
        self.layout.addWidget(self.StopButton, 4, 3)
        # Creating the canvas for plotting and the toolbar
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot(111)

        self.layout.addWidget(self.toolbar, 6, 0, 1, 2)
        self.layout.addWidget(self.canvas, 7, 0, 5, 5)
        self.setLayout(self.layout)

    def update_port(self, newport):
        self.PortNum = newport

    def is_process_running(self):
        return self.worker.isRunning()

    def Run_CMD(self):
        try:
            if self.I_NumCycles.text() == '' or self.I_StartVoltage.text() == '' or self.I_FirstVoltage.text() == '' or self.I_SecondVoltage.text() == '' or self.I_ScanRate.text() == '' or self.I_FileName.text() == '':
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Please fill in all the fields.")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            i = [i for i, radio_btn in enumerate(self.RangeGroup.buttons()) if radio_btn.isChecked()]
            k = [k for k, radio_btn in enumerate(self.CapGroup.buttons()) if radio_btn.isChecked()]
            self.Rindex = i[0]
            self.Cindex = k[0]
            if not i[0]:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Please select a current range.")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            if not k[0]:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Please select a capacitor range.")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            self.cycnum = int(self.I_NumCycles.text())
            self.startvolt = float(self.I_StartVoltage.text())
            self.firstvolt = float(self.I_FirstVoltage.text())
            self.secondvolt = float(self.I_SecondVoltage.text())
            self.scanrate = float(self.I_ScanRate.text())
            self.resistorval = int(ResistorValues[self.Rindex])
            self.CAPVal = int(CapacitorValues[self.Cindex])
            self.filename = self.I_FileName.text()

            if self.cycnum <= 0 or self.cycnum > 100:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Number of cycles must be between 1 and 100")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            if self.startvolt < -2.5 or self.startvolt > 2.5 or self.firstvolt < -2.5 or self.firstvolt > 2.5 or self.secondvolt < -2.5 or self.secondvolt > 2.5:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Start potential must be between -2.5 and +2.5 V")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            if self.scanrate <= 0.00001 or self.scanrate > 60:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Scan rate must be between 0.00001 and 60 V/s")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return
           
           
            self.idnum=1
            DAC1 = int(round(self.startvolt  * (DAC_QUANT * GAIN) + DAC_OFFSET))
            DAC2 = int(round(self.firstvolt  * (DAC_QUANT * GAIN) + DAC_OFFSET))
            DAC3 = int(round(self.secondvolt * (DAC_QUANT * GAIN) + DAC_OFFSET))
            self.numpoint = abs(DAC2 - DAC1) + abs(DAC3 - DAC2) + abs(DAC1 - DAC3)
            self.totpoint = self.numpoint * self.cycnum
            self.period = int(round(1e6 / (self.scanrate * DAC_QUANT)))

            if self.totpoint > 52000:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Total number of points is too large")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            

        except Exception as e:
            print(f"Error: {e}")
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

        transmit = f"{self.idnum},{DAC1},{DAC2},{DAC3},{self.period},{self.cycnum},{self.Rindex},{self.Cindex}\n"

        self.worker = CVWorker(transmit, self.PortNum)
        self.worker.data_ready.connect(self.update_plot)
        self.worker.start()
        self.processFlag= True

    def Stop_CMD(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.processFlag= False
            if self.serial_connection is not None:
                if self.serial_connection.is_open:
                
                    self.serial_connection.write(ResetCMD.encode("utf-8"))
                    self.serial_connection.close()

            print("Task terminated")

    def update_plot(self, Data):
        self.ax.clear()
        self.ax.plot(Data[:, 0], Data[:, 1])
        self.ax.grid(True)  # Add grid lines
        self.ax.set_xlabel("Voltage (V)")
        self.ax.set_ylabel(f"Current ({CurrentUnit[self.Rindex]})")
        self.canvas.draw()
        self.processFlag= False
        
    def update_port(self, newport):
        self.PortNum = newport

    def is_process_running(self):
        
        return self.processFlag 