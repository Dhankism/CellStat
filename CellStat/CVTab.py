# CVTab.py
from encodings.punycode import T
from tracemalloc import start
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
import os

from ping import *
from cailbration import *

BAUD_RATE = 115200
TIMEOUT = 30
ResetCMD="RESET\n"
serial_connection = None

idnum = 1  # ID number for the CV measurement (now global)

class CVWorker(QThread): # Worker thread for Cyclic Voltammetry (CV) measurements
    data_ready = pyqtSignal(np.ndarray)
    

    def __init__(self, transmit, filename, port_name, timeout):
        super().__init__()
        self.transmit = transmit
        self.port_name = port_name
        self.timeout = timeout
        self.filename = filename
        self.CycleData = []
        self.Data= []
    def run(self):
        try:
            global serial_connection
            # Open the serial connection
            print(str(self.port_name))
            serial_connection = serial.Serial(self.port_name, BAUD_RATE, timeout=self.timeout + 30)

            # Send the message to the Teensy
            message = self.transmit.encode("utf-8")
            serial_connection.reset_input_buffer()  # Clear any existing input buffer
            serial_connection.reset_output_buffer()  # Clear any existing output buffer
            serial_connection.write(message)
            print("You Transmitted:", self.transmit)
            print("estimated time for CV measurement:", self.timeout, "seconds")

            dataamount = 0
            self.Data = []
            self.CycleData = []  # List to store arrays for each cycle
            current_cycle = -1  # Track the current cycle index
            buffer = ""
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Start time for timeout
            time.sleep(1)

            # Loop to detect end of measurement message from Arduino
            while True:
                # Read all available lines as fast as possible
                while serial_connection.in_waiting > 0:
                    received = serial_connection.readline().decode("utf-8")
                    buffer += received
                    while "\n" in buffer:  # Split the buffer by newlines
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if line == "END":
                            print("Measurement completed")
                            serial_connection.close()
                            # Convert each cycle's data to np.array
                            self.CycleData = [np.array(cycle) for cycle in self.CycleData]
                            self.data_ready.emit(np.array(self.CycleData, dtype=object))
                            # Save data to CSV file here
                            self.save_cycles_to_csv(now, self.CycleData, self.filename)
                            return
                        if line.startswith("CYCLE_"):
                            cycle_num = int(line.split("_")[1])
                            # Start a new cycle array
                            self.CycleData.append([])
                            current_cycle += 1
                            print(f"Starting new cycle: {cycle_num}")
                            continue
                        if line:
                            print(line)
                            line = line.split(",")
                            try:
                                voltage = (int(line[0]) - DAC_OFFSET) * GAIN / DAC_QUANT
                                current = (int(line[1]) - ADC_OFFSET[2]) * ADC_QUANT * CurrentMultiplier[2] / ResistorValues[2]
                                print(voltage, ",", current)
                                dataamount += 1
                                self.CycleData[current_cycle].append([voltage, current])
                            except ValueError as e:
                                print(f"ValueError: {e}")
                                continue
                # Optional: short sleep to avoid 100% CPU usage
                time.sleep(0.001)
        except Exception as e:
            if serial_connection.is_open:
                print(f"Exception in CVWorker: {e}")
                
            return
        finally:
            if serial_connection.is_open:
                # Ensure the serial connection is closed properly
                serial_connection.close()

    def save_cycles_to_csv(self, now, CycleData, filename):
        # Ensure unique filename by appending _1, _2, etc. if file exists
        base, ext = os.path.splitext(filename)
        counter = 1
        unique_filename = filename
        while os.path.exists(unique_filename):
            unique_filename = f"{base}_{counter}{ext}"
            counter += 1

        try:
            with open(unique_filename, "w", newline="") as csvfile:
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
                writer.writerow([])

                # Prepare headers for each cycle
                headers = []
                for idx in range(len(CycleData)):
                    headers.extend([f"Cycle {idx+1} Voltage (V)", f"Cycle {idx+1} Current ({CurrentUnit[self.parent().Rindex]})"])
                writer.writerow(headers)

                # Find the max length of all cycles
                max_len = max(len(cycle) for cycle in CycleData)
                # Write data row by row, each cycle in its own columns
                for i in range(max_len):
                    row = []
                    for cycle in CycleData:
                        if i < len(cycle):
                            row.extend(cycle[i])
                        else:
                            row.extend(["", ""])  # Fill empty if this cycle is shorter
                    writer.writerow(row)
            print(f"Data saved to {unique_filename}")
        except Exception as e:
            print(f"Error saving CSV: {e}")

class CVTab(QWidget): 
    def __init__(self, port): # Main widget for the Cyclic Voltammetry (CV) tab
        super().__init__()
        self.layout = QGridLayout()
        global serial_connection
        
        
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
        self.I_NumCycles.setText("3")  # Default value for debugging

        self.L_StartVoltage = QLabel("Start Potential (V):")
        self.I_StartVoltage = QLineEdit()
        self.I_StartVoltage.setPlaceholderText("Enter the start potential between -2.5 and +2.5 V")
        self.I_StartVoltage.setText("0.0")  # Default value for debugging

        self.L_FirstVoltage = QLabel("First Inversion Potential (V):")
        self.I_FirstVoltage = QLineEdit()
        self.I_FirstVoltage.setPlaceholderText("Enter the first inversion potential")
        self.I_FirstVoltage.setText("-2.5")  # Default value for debugging

        self.L_SecondVoltage = QLabel("Second Inversion Potential (V):")
        self.I_SecondVoltage = QLineEdit()
        self.I_SecondVoltage.setPlaceholderText("Enter the second inversion potential")
        self.I_SecondVoltage.setText("2.5")  # Default value for debugging

        self.L_ScanRate = QLabel("Scan Rate (V/s):")
        self.I_ScanRate = QLineEdit()
        self.I_ScanRate.setPlaceholderText("Enter the scan rate")
        self.I_ScanRate.setText("2")  # Default value for debugging

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
        self.I_FileName.setText("debug_data.csv")  # Default value for debugging

        # Start and Stop and Save Buttons
        self.StartButton = QPushButton("Start")
        self.StartButton.clicked.connect(self.Run_CMD)
        self.StopButton = QPushButton("Stop")
        self.StopButton.clicked.connect(self.Stop_CMD)


        self.layout.addWidget(self.L_StartVoltage, 0, 0)
        self.layout.addWidget(self.I_StartVoltage, 0, 1)
        self.layout.addWidget(self.L_FirstVoltage, 1, 0)
        self.layout.addWidget(self.I_FirstVoltage, 1, 1)
        self.layout.addWidget(self.L_SecondVoltage, 2, 0)
        self.layout.addWidget(self.I_SecondVoltage, 2, 1)

        self.layout.addWidget(self.L_FileName, 0, 2)
        self.layout.addWidget(self.I_FileName, 0, 3)
        self.layout.addWidget(self.L_NumCycles, 1, 2)
        self.layout.addWidget(self.I_NumCycles, 1, 3)
        self.layout.addWidget(self.L_ScanRate, 2, 2)
        self.layout.addWidget(self.I_ScanRate, 2, 3)

       

        self.layout.addWidget(self.L_CurrentRange, 3, 0)
        self.layout.addLayout(self.RangeList, 3, 1, 1, 3)  # Adjusted to span multiple columns
        self.layout.addWidget(self.L_CapRange, 4, 0)
        self.layout.addLayout(self.CapList, 4, 1, 1, 3)
        self.layout.addWidget(self.StartButton, 5, 0, 1, 3)
        self.layout.addWidget(self.StopButton, 5, 3)
        # Creating the canvas for plotting and the toolbar
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot(111)

        self.layout.addWidget(self.toolbar, 6, 0, 1, 2)
        self.layout.addWidget(self.canvas, 7, 0, 5, 5)
        self.setLayout(self.layout)

        # After creating radio buttons for resistor and capacitor:
        if self.RangeGroup.buttons():
            self.RangeGroup.buttons()[3].setChecked(True)
        if self.CapGroup.buttons():
            self.CapGroup.buttons()[3].setChecked(True)

    def Run_CMD(self): # Start the Cyclic Voltammetry (CV) measurement
        try:
            # Get values from input fields and radio buttons
            global idnum
            i = [i for i, radio_btn in enumerate(self.RangeGroup.buttons()) if radio_btn.isChecked()]
            k = [k for k, radio_btn in enumerate(self.CapGroup.buttons()) if radio_btn.isChecked()]
            self.Rindex = i[0]
            self.Cindex = k[0]
            
            if not i:  # Check if any radio button is selected
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Please select a current range.")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            if not k:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Please select a capacitor range.")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return
            
            if self.I_NumCycles.text() == '' or self.I_StartVoltage.text() == '' or self.I_FirstVoltage.text() == '' or self.I_SecondVoltage.text() == '' or self.I_ScanRate.text() == '' or self.I_FileName.text() == '':
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Please fill in all the fields.")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return
            
            self.cycnum = int(self.I_NumCycles.text())
            self.startvolt = float(self.I_StartVoltage.text())
            self.firstvolt = float(self.I_FirstVoltage.text())
            self.secondvolt = float(self.I_SecondVoltage.text())
            self.scanrate = float(self.I_ScanRate.text())
            self.resistorval = int(ResistorValues[self.Rindex])
            self.CAPVal = float(CapacitorValues[self.Cindex])
            if self.I_FileName.text().endswith('.csv'):
                self.filename = self.I_FileName.text()  # Use the provided filename
            else:
                self.filename = self.I_FileName.text() + '.csv'  # Ensure the filename ends with .csv

            if self.cycnum < 0 or self.cycnum > 100:
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
           
            DAC1 = int(round(self.startvolt  * (DAC_QUANT * GAIN) + DAC_OFFSET))
            DAC2 = int(round(self.firstvolt  * (DAC_QUANT * GAIN) + DAC_OFFSET))
            DAC3 = int(round(self.secondvolt * (DAC_QUANT * GAIN) + DAC_OFFSET))
            self.numpoint = abs(DAC2 - DAC1) + abs(DAC3 - DAC2) + abs(DAC1 - DAC3)
            self.totpoint = self.numpoint * self.cycnum
            self.period = int(round(1e6 / (self.scanrate * DAC_QUANT))) # in microseconds

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

        transmit = f"{idnum},{DAC1},{DAC2},{DAC3},{self.period},{self.cycnum},{self.Rindex},{self.Cindex}\n"
        #run the worker thread to start the CV measurement

        # guess the amout of time the CV measurement will take
        estimated_time = self.totpoint * self.period * 1e-6  # in seconds

        self.worker = CVWorker(transmit, self.filename, self.PortNum, estimated_time)
        self.worker.setParent(self)  # So worker can access parent attributes for CSV
        self.worker.data_ready.connect(self.update_plot)  # Update the plot with data from worker when ready
        self.worker.start()
        self.processFlag = True

    def Stop_CMD(self): # Stop the Cyclic Voltammetry (CV) measurement
        if self.worker is not None and self.worker.isRunning():
            self.worker.terminate() #stop the worker thread
            self.worker.wait() # wait for the thread to finish dont know if needed just to be sure
            self.processFlag= False
            if serial_connection is not None: # Check if serial connection exists and close it if isd
                if serial_connection.is_open:

                    serial_connection.write(ResetCMD.encode("utf-8"))
                    serial_connection.close()
                    print("Task terminated")
            else:
                print("No active serial connection to terminate")


    def update_plot(self): # Update the plot with the data received from the worker thread
        self.ax.clear()

            # Plot each cycle with a legend
        for idx, cycle in enumerate(self.worker.CycleData):
            if len(cycle) > 0:
                cycle = np.array(cycle)
                self.ax.plot(cycle[:, 0], cycle[:, 1], label=f"Cycle {idx+1}")
        self.ax.legend()
     
            # If no CycleData, plot the raw data
        
        self.ax.grid(True)  # Add grid lines
        self.ax.minorticks_on()  # Enable minor ticks
        self.ax.grid(True, which='minor', linestyle=':', linewidth=0.5)  # Add minor grid lines
        self.ax.set_xlabel("Voltage (V)")
        self.ax.set_ylabel(f"Current ({CurrentUnit[self.Rindex]})")
        self.canvas.draw()

        # Reset the worker and process flag
        self.processFlag = False

    def update_port(self, newport): # Update the port number for the serial connection
        self.PortNum = newport

    def is_process_running(self): # Check if the worker thread is running
        return self.processFlag
