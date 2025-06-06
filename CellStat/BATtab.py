# BATtab.py
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

class BATWorker(QThread): # Worker thread for Battery Test measurements
    
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
            self.CycleData = [[]]  # Ensure at least one list for SWV data (no cycles)
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
                        if line:
                            print(line)
                            line = line.split(",")
                            try:
                                measured_time = int(line[0])
                                current = (int(line[1]) - ADC_OFFSET[2]) * ADC_QUANT * CurrentMultiplier[2] / ResistorValues[2]
                                print(measured_time, ",", current)
                                dataamount += 1
                                self.CycleData[0].append([measured_time, current])  # Always append to the first (and only) cycle
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
        # Save the CSV file inside the folder specified by 'filename'
        currentdirectory = os.getcwd()
        # Compose the CSV file name (e.g., BAT_data_1.csv, BAT_data_2.csv, etc.)
        # Find a unique filename by incrementing a counter if file exists
        base = os.path.basename(filename)
        counter = 1
        while True:
            csv_filename = f"{base}_{counter}.csv"
            file_path = os.path.join(currentdirectory, filename, csv_filename)
            if not os.path.exists(file_path):
                break
            counter += 1
        # Save inside the folder
        file_path = os.path.join(currentdirectory, filename, csv_filename)

        try:
            with open(file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                # Write test info as header
                writer.writerow([f"Test Time: {now}"])
                writer.writerow([f"Number of pulses: {self.parent().cycnum}"])
                writer.writerow([f"Start potential: {self.parent().startvolt} V"])
                writer.writerow([f"Step potential: {self.parent().stepvolt} V"])
                writer.writerow([f"Start time: {self.parent().starttime} s"])
                writer.writerow([f"Step time: {self.parent().steptime} s"])
                writer.writerow([f"Scan rate: {self.parent().scanrate} Hz"])
                writer.writerow([f"Resistor value: {CurrentRange[self.parent().Rindex]}"])
                writer.writerow([f"Capacitor value: {self.parent().CAPVal} F"])
                writer.writerow([])

                # Write SWV headers (no cycles)
                writer.writerow(["Time (us)", "Current (A)"])

                # Write data: CycleData[0] contains all [time, current] pairs
                for row in CycleData[0]:
                    writer.writerow(row)
            print(f"Data saved to {file_path}")
        except Exception as e:
            print(f"Error saving CSV: {e}")

class BATTab(QWidget): 
    def __init__(self, port): # Main widget for the Battery Test tab
        super().__init__()
        self.layout = QGridLayout()
        global serial_connection
        # Label and Line Edit for BAT Tab
        i = QLabel("BAT Tab")
        self.PortNum = port
        self.worker = None
        self.processFlag= False

        # Battery Test parameters
        # L = Label
        # I = Input
        self.L_NumCycles = QLabel("Number of Pulses:")
        self.I_NumCycles = QLineEdit()
        self.I_NumCycles.setPlaceholderText("Enter the number of pulses (1-10)")
        #self.I_NumCycles.setText("3")  # Default value for debugging

        self.L_StartVoltage = QLabel("Start Potential (V):")
        self.I_StartVoltage = QLineEdit()
        self.I_StartVoltage.setPlaceholderText("Enter the start potential between -2.5 and +2.5 V")
        #self.I_StartVoltage.setText("0.0")  # Default value for debugging

        self.L_StepVoltage = QLabel("Step Potential (V):")
        self.I_StepVoltage = QLineEdit()
        self.I_StepVoltage.setPlaceholderText("Enter the step potential between -2.5 and +2.5 V")
        #self.I_StepVoltage.setText("-2.5")  # Default value for debugging

        self.L_StartTime = QLabel("Start Time (s):")
        self.I_StartTime = QLineEdit()
        self.I_StartTime.setPlaceholderText("Enter the start time in seconds")
        #self.I_StartTime.setText("2")  # Default value

        self.L_StepTime = QLabel("Step Time (s):")
        self.I_StepTime = QLineEdit()
        self.I_StepTime.setPlaceholderText("Enter the step time in seconds")
        #self.I_StepTime.setText("2")  # Default value


        self.L_ScanRate = QLabel("Scan Rate (Hz):")
        self.I_ScanRate = QLineEdit()
        self.I_ScanRate.setPlaceholderText("Enter the scan rate")
        #self.I_ScanRate.setText("10")  # Default value for debugging

        self.L_TimeInterval = QLabel("Time Interval (s):")
        self.I_TimeInterval = QLineEdit()
        self.I_TimeInterval.setPlaceholderText("Enter the test interval in seconds")
        #self.I_TimeInterval.setText("30")  # Default value for debugging

        self.L_TestAmount = QLabel(" Amount of test to be done:")
        self.I_TestAmount = QLineEdit()
        self.I_TestAmount.setPlaceholderText("Enter the amount of test to be done")
        #self.I_TestAmount.setText("3")  # Default value for debugging


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
        self.I_FileName.setPlaceholderText("Enter a name for the folder")
        self.I_FileName.setText("BAT_data")  # Default value for debugging

   
        # Start and Stop and Save Buttons
        self.StartButton = QPushButton("Start")
        self.StartButton.clicked.connect(self.Run_CMD)
        self.StopButton = QPushButton("Stop")
        self.StopButton.clicked.connect(self.Stop_CMD)


        self.layout.addWidget(self.L_StartVoltage, 0, 0)
        self.layout.addWidget(self.I_StartVoltage, 0, 1)
        self.layout.addWidget(self.L_StepVoltage, 1, 0)
        self.layout.addWidget(self.I_StepVoltage, 1, 1)
      

        self.layout.addWidget(self.L_FileName, 0, 2)
        self.layout.addWidget(self.I_FileName, 0, 3)
        self.layout.addWidget(self.L_NumCycles, 1, 2)
        self.layout.addWidget(self.I_NumCycles, 1, 3)
        self.layout.addWidget(self.L_ScanRate, 2, 2)
        self.layout.addWidget(self.I_ScanRate, 2, 3)
        self.layout.addWidget(self.L_TestAmount, 3, 2)
        self.layout.addWidget(self.I_TestAmount, 3, 3)


        self.layout.addWidget(self.L_StartTime, 2, 0)
        self.layout.addWidget(self.I_StartTime, 2, 1)
        self.layout.addWidget(self.L_StepTime, 3, 0)
        self.layout.addWidget(self.I_StepTime, 3, 1)
        self.layout.addWidget(self.L_TimeInterval, 4, 0)
        self.layout.addWidget(self.I_TimeInterval, 4, 1)
        
        self.layout.addWidget(self.L_CurrentRange, 5, 0)
        self.layout.addLayout(self.RangeList, 5, 1, 1, 3)  # Adjusted to span multiple columns
        self.layout.addWidget(self.L_CapRange, 6, 0)
        self.layout.addLayout(self.CapList, 6, 1, 1, 3)
        self.layout.addWidget(self.StartButton, 7, 0, 1, 3)
        self.layout.addWidget(self.StopButton, 7, 3)
        # Creating the canvas for plotting and the toolbar
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot(111)

        self.layout.addWidget(self.toolbar, 8, 0, 1, 2)
        self.layout.addWidget(self.canvas, 9, 0, 5, 5)
        self.setLayout(self.layout)

        # After creating radio buttons for resistor and capacitor:
        if self.RangeGroup.buttons():
            self.RangeGroup.buttons()[3].setChecked(True)
        if self.CapGroup.buttons():
            self.CapGroup.buttons()[3].setChecked(True)

    def Run_CMD(self): # Start the Battery Test measurement
        try:
          
            # Get values from input fields and radio buttons
            
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

            if self.I_NumCycles.text() == '' or self.I_StartVoltage.text() == '' or self.I_StepVoltage.text() == '' or self.I_StartTime.text() == '' or self.I_StepTime.text() == '' or self.I_ScanRate.text() == '' or self.I_FileName.text() == '' or self.I_TimeInterval.text() == '' or self.I_TestAmount.text() == '':
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Please fill in all the fields.")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return
            
            self.cycnum = int(self.I_NumCycles.text())
            self.startvolt = float(self.I_StartVoltage.text())
            self.stepvolt = float(self.I_StepVoltage.text())
            self.starttime = float(self.I_StartTime.text())
            self.steptime = float(self.I_StepTime.text())
            self.scanrate = float(self.I_ScanRate.text())
            self.downtime = int(self.I_TimeInterval.text())
            self.maxtests = int(self.I_TestAmount.text())
            self.resistorval = int(ResistorValues[self.Rindex])
            self.CAPVal = float(CapacitorValues[self.Cindex])
            self.filename = self.I_FileName.text()  # Use the provided filename

            if not self.filename:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Please enter a valid folder name.")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            if self.cycnum < 0 or self.cycnum > 10:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Number of cycles must be between 1 and 10")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            if self.startvolt < -2.5 or self.startvolt > 2.5 or self.stepvolt < -2.5 or self.stepvolt > 2.5 :
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Potential must be between -2.5 and +2.5 V")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

            if self.scanrate <= 0.00001 or self.scanrate > 60:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Scan rate must be between 0.00001 and 60 Hz")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return
            
            if self.maxtests <= 0 :
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Test amount must be greater than 0")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return
            
            if self.downtime <= 0 or self.downtime < (self.cycnum * (self.starttime + self.steptime+ 5)+ self.starttime):
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Time interval must be greater than 0 and greater than the total time of the test")
                error_dialog.setInformativeText(f"Total time of one test is {self.cycnum * (self.starttime + self.steptime+ 5)+ self.starttime} seconds")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return
           
           
            self.idnum=2 # ID number for the BAT measurement
            DAC1 = int(round(self.startvolt  * (DAC_QUANT * GAIN) + DAC_OFFSET))
            DAC2 = int(round(self.stepvolt  * (DAC_QUANT * GAIN) + DAC_OFFSET))
            T1= int(round(self.starttime * 1e6))  # Convert seconds to microseconds
            T2 = int(round(self.steptime * 1e6))  # Convert seconds to microseconds
           
            self.scanrate = int(round(1/self.scanrate * 1e6))  # in microseconds
            self.totpoint = ((self.cycnum *(T1+T2))+ T1) / self.scanrate  # Total number of points to be sent

            if self.totpoint > 52000: #this is the maximum number of points that can be sent by the Teensy
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("Total number of points is too large")
                error_dialog.setWindowTitle("Input Error")
                error_dialog.exec_()
                return

        except Exception as e:
            print(f"Error: {e}")
            return

        print("Running BAT with the following parameters:")
        print(f"Number of cycles: {self.cycnum}")
        print(f"Start potential: {self.startvolt}")
        print(f"Step potential: {self.stepvolt}")
        print(f"Start time: {self.starttime}")
        print(f"Step time: {self.steptime}")
        print(f"Scan rate: {self.scanrate}")
        print(f"Time interval: {self.downtime}")
        print(f"Test amount: {self.maxtests}")
        print(f"Resistor value: {self.resistorval}")
        print(f"Capacitor value: {self.CAPVal}")
        print(f"Filename: {self.filename}")

        #make a folder using the file name if it does exist add _#
        if not os.path.exists(self.filename):
                # If it doesn't exist, create it
            os.makedirs(self.filename)
            self.folder_name =f"{self.filename}"
        else:
                # If it exists, find a new name by adding a number
            i = 1
            while os.path.exists(f"{self.filename}_{i}"):
                    i += 1
            os.makedirs(f'{self.filename}_{i}')
            self.foldername =f'{self.filename}_{i}'

        print(f'Folder {self.foldername} created.')
        self.foldername = os.path.abspath(self.foldername)#make it a directory

        self.transmit = f"{self.idnum},{DAC1},{DAC2},{T1},{T2},{self.scanrate},{self.cycnum},{self.Rindex},{self.Cindex}\n"
     
        # guess the amout of time the BAT measurement will take
        self.estimated_time = self.totpoint * self.scanrate * 1e-6  # in seconds

        self.test_count = 1

        self.run_data()  # Run the first test immediately

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_data)
        self.timer.start(1000 * self.downtime)  # Repeat every downtime seconds
        self.processFlag = True



    def run_data(self): #this is just used to run the worker thread and check if the test is done and count the tests
        if self.test_count >= self.maxtests:
            self.timer.stop()
            print("All tests completed.")
            return

        # Place your test-starting logic here (from Run_CMD)
        # For example:
        self.worker = BATWorker(self.transmit, self.foldername, self.PortNum, self.estimated_time)
        self.worker.setParent(self)
        self.worker.data_ready.connect(self.update_plot)
        self.worker.start()
       

        self.test_count += 1


    

    def Stop_CMD(self): # Stop the Battery Test measurement
        if self.worker is not None and self.worker.isRunning():
            self.worker.terminate() #stop the worker thread
            self.worker.wait() # wait for the thread to finish dont know if needed just to be sure
            
            if serial_connection is not None: # Check if serial connection exists and close it if isd
                if serial_connection.is_open:

                    serial_connection.write(ResetCMD.encode("utf-8"))
                    serial_connection.close()
                    print("Task terminated")
            else:
                print("No active serial connection to terminate")
        self.timer.stop()  # Stop the timer if it exists
        print("Battery Test stopped")
        # Reset the worker and test count
        self.test_count = 0
        self.processFlag= False

        


    def update_plot(self): # Update the plot with the data received from the worker thread
        self.ax.clear()

        # Plot time (us) vs current for BAT (no cycles)
        if len(self.worker.CycleData) > 0 and len(self.worker.CycleData[0]) > 0:
            data = np.array(self.worker.CycleData[0])
            self.ax.plot(data[:, 0], data[:, 1])
        
        self.ax.grid(True)  # Add grid lines
        self.ax.minorticks_on()  # Enable minor ticks
        self.ax.grid(True, which='minor', linestyle=':', linewidth=0.5)  # Add minor grid lines
        self.ax.set_xlabel("Time (us)")
        self.ax.set_ylabel(f"Current ({CurrentUnit[self.Rindex]})")
        self.canvas.draw()

        # Reset the worker and process flag
        self.processFlag = False
        
        #save the plot as an image
        currentdirectory = os.getcwd()
        # Compose the CSV file name (e.g., BAT_data_1.csv, BAT_data_2.csv, etc.)
        # Find a unique filename by incrementing a counter if file exists
        base = os.path.basename(self.foldername)
        counter = 1
        while True:
            png_filename = f"{base}_{counter}.png"
            file_path = os.path.join(currentdirectory, self.foldername, png_filename)
            if not os.path.exists(file_path):
                break
            counter += 1
        # Save inside the folder
        file_path = os.path.join(currentdirectory, self.foldername, png_filename)
        # Save the plot as an image
        self.figure.savefig(file_path)


    def update_port(self, newport): # Update the port number for the serial connection
        self.PortNum = newport

    def is_process_running(self): # Check if the worker thread is running
        return self.processFlag
