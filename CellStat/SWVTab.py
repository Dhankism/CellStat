# SWVTab.py

from turtle import st
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
import csv  # Add this import at the top

from ping import *
from cailbration import *

BAUD_RATE = 115200
TIMEOUT = 30
ResetCMD="RESET\n"

class SWVWorker(QThread): # Worker thread for Square Wave Voltammetry (SWV) measurements
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
            CycleData = []  # List to store arrays for each cycle
            current_cycle = -1  # Track the current cycle index
            buffer = ""
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename = self.parent().I_FileName.text()
            start_time = time.time()  # Start time for timeout
            time.sleep(10)
            # Loop to detect end of measurement message from Arduino
            while True:
                while (self.serial_connection.in_waiting == 0 and (time.time() - start_time) > 40): # Wait for data or timeout after 40 seconds
                    pass

                received = self.serial_connection.readline().decode("utf-8")
                buffer += received
                while "\n" in buffer:  # Split the buffer by newlines
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line == "END":
                        print("Measurement completed")
                        self.serial_connection.close()
                        Data = np.array(Data)
                        # Convert each cycle's data to np.array
                        CycleData = [np.array(cycle) for cycle in CycleData]
                        self.data_ready.emit(Data)
                        # Save data to CSV file here
                        self.save_cycles_to_csv(now, CycleData, filename)
                        return
                    if line.startswith("CYCLE_"):
                        try:
                            cycle_num = int(line.split("_")[1])
                            # Start a new cycle array
                            CycleData.append([])
                            current_cycle += 1
                            print(f"Starting new cycle: {cycle_num}")
                        except Exception as e:
                            print(f"Cycle marker parse error: {e}")
                        continue
                    if line:
                        print(line)
                        line = line.split(",")
                        try:
                            voltage = (int(line[0]) - DAC_OFFSET) * GAIN / DAC_QUANT
                            current = (int(line[1]) - ADC_OFFSET[2]) * ADC_QUANT * CurrentMultiplier[2] / ResistorValues[2]
                            print(voltage, ",", current)
                            Data.append([voltage, current])
                            dataamount += 1
                            # Store in current cycle if a cycle has started
                            if current_cycle >= 0:
                                CycleData[current_cycle].append([voltage, current])
                        except ValueError as e:
                            print(f"ValueError: {e}")
                            continue
        except Exception as e:
            if self.serial_connection.is_open:
                self.serial_connection.write(ResetCMD.encode("utf-8"))
                self.serial_connection.close()
            print(f"Exception in CVWorker: {e}")
        finally:
            if self.serial_connection.is_open:
                # Ensure the serial connection is closed properly
                self.serial_connection.close()

    def save_cycles_to_csv(self, now, CycleData, filename):
        # Save each cycle's data in one CSV file, separated by cycle number, with headers and units
        try:
            with open(filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                # Write test info as header
                writer.writerow([f"Test Time: {now}"])
                writer.writerow([f"Number of cycles: {self.parent().cycnum}"])
                writer.writerow([f"Start potential: {self.parent().startvolt} V"])
                writer.writerow([f"First inversion potential: {self.parent().firstvolt} V"])
                writer.writerow([f"Second inversion potential: {self.parent().secondvolt} V"])
                writer.writerow([f"Scan rate: {self.parent().scanrate} V/s"])
                writer.writerow([f"Resistor value: {CurrentRange[self.parent().Rindex]}"])
                writer.writerow([f"Capacitor value: {self.parent().CAPVal} F"])
                writer.writerow([f"Filename: {filename}"])
                writer.writerow([])

                for idx, cycle in enumerate(CycleData):
                    writer.writerow([f"Cycle {idx+1}"])
                    writer.writerow(["Voltage (V)", f"Current ({CurrentUnit[self.parent().Rindex]})"])
                    for row in cycle:
                        writer.writerow(row)
                    writer.writerow([])  # Blank line between cycles
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving CSV: {e}")

class SWVTab(QWidget): 
    def __init__(self, port): # Main widget for the Square Wave Voltammetry (SWV) tab
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
        self.L_NumCycles = QLabel("Number of pulses:")
        self.I_NumCycles = QLineEdit()
        self.I_NumCycles.setPlaceholderText("Enter the number of pulses")

        self.L_StartVoltage = QLabel("Start Potential (V):")
        self.I_StartVoltage = QLineEdit()
        self.I_StartVoltage.setPlaceholderText("Enter the start potential between -2.5 and +2.5 V")

        self.L_StartTime = QLabel("Start Time (s):")
        self.I_StartTime = QLineEdit()
        self.I_StartTime.setPlaceholderText("Enter the start time in seconds")

        self.L_StepVoltage = QLabel("Step Potential (V):")
        self.I_StepVoltage = QLineEdit()
        self.I_StepVoltage.setPlaceholderText("Enter the step potential between -2.5 and +2.5 V")

        self.L_StepTime = QLabel("Step Time (s):")
        self.I_StepTime = QLineEdit()
        self.I_StepTime.setPlaceholderText("Enter the step time in seconds")

        self.L_ScanRate = QLabel("Scan Rate (Hz):")
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
        self.layout.addWidget(self.L_StartTime, 1, 2)
        self.layout.addWidget(self.I_StartTime, 1, 3)
        self.layout.addWidget(self.L_StepVoltage, 2, 0)
        self.layout.addWidget(self.I_StepVoltage, 2, 1)
        self.layout.addWidget(self.L_StepTime, 2, 2)
        self.layout.addWidget(self.I_StepTime, 2, 3)
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


    def Run_CMD(self): # Start the square wave (SWV) measurement
        try:
            if self.I_NumCycles.text() == '' or self.I_StartVoltage.text() == '' or self.I_StepVoltage.text() == '' or self.I_ScanRate.text() == '' or self.I_FileName.text() == '':
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
            self.stepvolt = float(self.I_StepVoltage.text())
            self.starttime = float(self.I_StartTime.text())  # Convert to seconds
            self.steptime = float(self.I_StepTime.text())  # Convert to seconds
            self.scanrate = float(self.I_ScanRate.text())  # Convert to Hz
            self.resistorval = int(ResistorValues[self.Rindex])
            self.CAPVal = int(CapacitorValues[self.Cindex])
            self.filename = self.I_FileName.text()

            if self.starttime < 0 or self.steptime < 0:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Start time and step time must be non-negative")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            if self.cycnum <= 0 or self.cycnum > 100:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Number of cycles must be between 1 and 100")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            if self.startvolt < -2.5 or self.startvolt > 2.5 or self.stepvolt < -2.5 or self.stepvolt > 2.5 :
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Start potential must be between -2.5 and +2.5 V")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            if self.scanrate <= 0.00001 or self.scanrate > 100:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Scan rate must be between 0.00001 and 100 Hz")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return
           
           
            self.idnum = 2 # ID number for the Teensy to know its SWV
            self.period = 1/ self.scanrate * 1000 # Calculate the period in milliseconds
            DAC1 = int(round(self.startvolt  * (DAC_QUANT * GAIN) + DAC_OFFSET))
            DAC2 = int(round(self.stepvolt  * (DAC_QUANT * GAIN) + DAC_OFFSET))
            T1 = self.starttime * self.period # Convert to amout to scan will be done in milliseconds
            T2 = self.steptime * self.period # Convert to amout to scan will be done in milliseconds
            self.numpoint = self.period* (self.starttime + self.steptime) # Convert to milliseconds
            self.totpoint = self.numpoint * self.cycnum

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
        print(f"Step potential: {self.stepvolt}")
        print(f"start time: {self.I_StartTime.text()} s")
        print(f"Step time: {self.I_StepTime.text()} s")
        print(f"Scan rate: {self.scanrate}")
        print(f"Resistor value: {self.resistorval}")
        print(f"Capacitor value: {self.CAPVal}")
        print(f"Filename: {self.filename}")

        transmit = f"{self.idnum},{DAC1},{DAC2}, {T1},{T2},{self.period},{self.cycnum},{self.Rindex},{self.Cindex}\n"

        self.worker = SWVWorker(transmit, self.PortNum)
        self.worker.setParent(self)  # So worker can access parent attributes for CSV
        self.worker.data_ready.connect(self.update_plot)
        self.worker.start()
        self.processFlag= True

    def Stop_CMD(self): # Stop the SWV measurement
        if self.worker is not None and self.worker.isRunning():
            self.worker.terminate() #stop the worker thread
            self.worker.wait() # wait for the thread to finish
            self.processFlag= False
            if self.serial_connection is not None: # Check if serial connection exists and close it if isd
                if self.serial_connection.is_open:
                
                    self.serial_connection.write(ResetCMD.encode("utf-8"))
                    self.serial_connection.close()

            print("Task terminated")

    def update_plot(self, Data): # Update the plot with the data received from the worker thread
        self.ax.clear()
        # Check if CycleData exists as an attribute (set by the worker)
        if hasattr(self.worker, "CycleData") and self.worker.CycleData:
            # Plot each cycle with a legend
            for idx, cycle in enumerate(self.worker.CycleData):
                if len(cycle) > 0:
                    cycle = np.array(cycle)
                    self.ax.plot(cycle[:, 0], cycle[:, 1], label=f"Cycle {idx+1}")
            self.ax.legend()
        else:
            # Fallback: plot all data if no cycle info
            self.ax.plot(Data[:, 0], Data[:, 1], label="All Data")
        self.ax.grid(True)  # Add grid lines
        self.ax.set_xlabel("Voltage (V)")
        self.ax.set_ylabel(f"Current ({CurrentUnit[self.Rindex]})")
        self.canvas.draw()
        self.processFlag = False

    def update_port(self, newport): # Update the port number for the serial connection
        self.PortNum = newport

    def is_process_running(self): # Check if the worker thread is running
        return self.worker.isRunning()
