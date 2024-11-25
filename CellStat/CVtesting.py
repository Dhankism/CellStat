import math
import matplotlib.pyplot as plt
import numpy as np
import serial
import sys
import csv
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from find_teensy_port import *


class CvMethod(QWidget):
    # Class variables
    BAUD_RATE = 115200
    TIMEOUT = 3

    # Parameters for conversion between numeric and analog values
    # Extracted from the calibration process
    DAC_TEENSY_QUANT = 830.725
    DAC_TEENSY_OFFSET = 2085
    ADC_TEENSY_QUANT = 3.3 / 4095
    ADC_TEENSY_OFFSET = 2070
    TEENSY_CONV_COEFF = 1.51  # Inverse of the output voltage divider
    GAIN = -1.0  # To get the current according to the IUPAC convention

    TEENSY_STAB_DELAY = 2.0  # Stabilization time before starting CV
    RTIA = 100  # Default RTIA resistor value converting current to voltage, in KΩ

    def __init__(self, port):
        self.port_board = port
        super().__init__()  # Initializing QWidget (using super() as we inherit from QWidget)

        main_layout = QVBoxLayout()

        # Creating the input parameters group
        input_group_box = QGroupBox("Input Parameters")
        input_layout = QGridLayout()

        # Creating the file parameters group
        file_group_box = QGroupBox("File")
        file_layout = QHBoxLayout()

        # RTIA parameters
        self.label_rtia = QLabel("RTIA value (kΩ):")
        self.input_rtia = QLineEdit()
        self.input_rtia.setPlaceholderText("Default: 100")

        # File parameters
        self.label_file = QLabel("File Name:")
        self.input_file = QLineEdit()
        self.input_file.setPlaceholderText("Enter the CSV file name if you want to save the data")
        file_layout.addWidget(self.label_file)
        file_layout.addWidget(self.input_file)
        file_group_box.setLayout(file_layout)

        # Cyclic Voltammetry (CV) parameters
        self.label_num_cycles = QLabel("Number of Cycles:")
        self.input_num_cycles = QLineEdit()
        self.input_num_cycles.setPlaceholderText("Enter the number of cycles")

        self.label_start_potential = QLabel("Start Potential (V):")
        self.input_start_potential = QLineEdit()
        self.input_start_potential.setPlaceholderText("Enter the start potential between -2.4 and +2.4 V")

        self.label_first_inversion = QLabel("First Inversion Potential (V):")
        self.input_first_inversion = QLineEdit()
        self.input_first_inversion.setPlaceholderText("Enter the first inversion potential")

        self.label_second_inversion = QLabel("Second Inversion Potential (V):")
        self.input_second_inversion = QLineEdit()
        self.input_second_inversion.setPlaceholderText("Enter the second inversion potential")

        self.label_scan_rate = QLabel("Scan Rate (V/s):")
        self.input_scan_rate = QLineEdit()
        self.input_scan_rate.setPlaceholderText("Enter the scan rate")

        # Placing widgets in the layout
        input_layout.addWidget(self.label_rtia, 0, 0)
        input_layout.addWidget(self.input_rtia, 0, 1)
        input_layout.addWidget(self.label_num_cycles, 1, 0)
        input_layout.addWidget(self.input_num_cycles, 1, 1)
        input_layout.addWidget(self.label_start_potential, 2, 0)
        input_layout.addWidget(self.input_start_potential, 2, 1)
        input_layout.addWidget(self.label_first_inversion, 3, 0)
        input_layout.addWidget(self.input_first_inversion, 3, 1)
        input_layout.addWidget(self.label_second_inversion, 4, 0)
        input_layout.addWidget(self.input_second_inversion, 4, 1)
        input_layout.addWidget(self.label_scan_rate, 5, 0)
        input_layout.addWidget(self.input_scan_rate, 5, 1)

        input_group_box.setLayout(input_layout)

        # Creating the start button
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px;")
        self.start_button.clicked.connect(self.check_params)

        # Creating the canvas for plotting and the toolbar
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot(111)

        # Adding widgets to the main layout
        main_layout.addWidget(input_group_box)
        main_layout.addWidget(file_group_box)
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)
        self.setWindowTitle("CV Method")
        self.setGeometry(600, 150, 800, 800)

    def closeEvent(self, event):
        close_dialog = QMessageBox()
        close_dialog.setText("Are you sure?")
        close_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        user_choice = close_dialog.exec()

        if user_choice == QMessageBox.Yes:
            event.accept()
            self.Arduino_Serial.close()
        else:
            event.ignore()

    def check_params(self):
        # Error handling
        error_detected = False
        try:
            start_potential = float(self.input_start_potential.text())
            first_inversion = float(self.input_first_inversion.text())
            second_inversion = float(self.input_second_inversion.text())
            num_cycles = int(self.input_num_cycles.text())
            scan_rate = float(self.input_scan_rate.text())
            # Default RTIA value
            if self.input_rtia.text() == "":
                self.input_rtia.setText(str(self.RTIA))
            self.RTIA = float(self.input_rtia.text()) * 1000

            # Limiting the number of cycles to 100
            if num_cycles <= 0 or num_cycles > 100:
                self.show_error_message('Number of cycles should be between 1 and 100')
                error_detected = True

            # Checking potentials
            if abs(start_potential) > 2.4 or abs(first_inversion) > 2.4 or abs(second_inversion) > 2.4:
                self.show_error_message('Potentials should be between -2.4 and 2.4 V')
                error_detected = True

            # Checking scan rate
            if scan_rate <= 0.001 or scan_rate > 100:
                self.show_error_message('Scan rate should be between 0.001 and 100 V/s')
                error_detected = True

            period = round(1e6 / (scan_rate * self.DAC_TEENSY_QUANT))  # Conversion to microseconds

            str_start_potential = str(self.voltage_to_dac(start_potential))  # Calculate DAC code for Vstart
            str_first_inversion = str(self.voltage_to_dac(first_inversion))  # Calculate DAC code for the first Vstop
            str_second_inversion = str(self.voltage_to_dac(second_inversion))  # Calculate DAC code for the second Vstop

            num_points = 2 * abs(int(str_first_inversion) - int(str_second_inversion)) + 1  # Number of points in a CV
            total_points = num_cycles * num_points  # Total number of points

            if total_points > 52000:
                self.show_error_message('Total number of points > 52000, reduce number of cycles or scans')
                error_detected = True

            print("Scan rate", scan_rate)
            print("Number of points", total_points)

        except:
            self.show_error_message("Values must be entered and they must be correct!")
            error_detected = True

        if not error_detected:  # Start main method only if there are no errors in parameters
            # Calculate acquisition time
            cv_time = self.TEENSY_STAB_DELAY + period * total_points / 1e6
            print("Time for CV + 2s waiting time in Arduino:", cv_time)
            transmit = f"{str_start_potential},{str_first_inversion},{str_second_inversion},{str(period)},{str(num_cycles)},{self.DAC_TEENSY_OFFSET}"
            self.run_main(transmit, num_points, num_cycles)

    def run_main(self, transmit, num_points, num_cycles):
        Arduino_Serial = serial.Serial(self.port_board, self.BAUD_RATE, timeout=self.TIMEOUT)

        # Send CV parameters to Teensy to start measurement
        message = transmit.encode("utf-8")
        Arduino_Serial.write(message)
        print("You Transmitted:", transmit)

        # Loop to detect end of measurement message from Arduino
        while True:
            received = Arduino_Serial.readline()[:-2]
            received_utf8 = received.decode("utf-8")
            if received_utf8 == "Measurement Ended":
                break

        # Retrieve and store data
        data_array = np.zeros((num_points, num_cycles + 1), float)
        for k in range(1, num_cycles + 1):
            for j in range(num_points):
                data = Arduino_Serial.readline()[:-2]
                data_utf8 = data.decode("utf-8")
                line = data_utf8.split(",")
                data_array[j, 0] = self.dac_to_voltage(int(line[0]))
                data_array[j, k] = self.adc_to_current(int(line[1]))

        # Determine the most representative unit
        unit, coef_unit = self.determine_current_unit(data_array[:, 1])

        Arduino_Serial.close()  # Close serial connection
        self.ax.clear()  # Clear axes for new plot
        for k in range(1, num_cycles + 1):
            data_array[:, k] *= coef_unit
            self.ax.plot(data_array[:, 0], data_array[:, k], label="Cycle " + str(k))

        self.ax.grid(True)
        self.ax.legend()
        self.ax.set_xlabel("E (V) vs Ref")
        self.ax.set_ylabel("I (" + unit + ")")
        self.canvas.draw()

        # Save results to a CSV file if the user desires
        if self.input_file.text() != "":
            self.save_results(f"{self.input_file.text()}.csv", data_array)

    def save_results(self, filename, data_array):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Potential (V)', 'Current (A)'])
            for row in data_array:
                writer.writerow(row)

    def voltage_to_dac(self, voltage):
        return int(round(voltage * self.DAC_TEENSY_QUANT * self.GAIN + self.DAC_TEENSY_OFFSET))

    def dac_to_voltage(self, dac):
        return (dac - self.DAC_TEENSY_OFFSET) / (self.GAIN * self.DAC_TEENSY_QUANT)

    def adc_to_current(self, adc):
        return (adc - self.ADC_TEENSY_OFFSET) * self.ADC_TEENSY_QUANT * self.TEENSY_CONV_COEFF / self.RTIA

    def determine_current_unit(self, data):
        percentile_current = np.percentile(np.abs(data), 95)
        if percentile_current >= 1:
            return "A", 1
        elif percentile_current >= 1e-3:
            return "mA", 1e3
        elif percentile_current >= 1e-6:
            return "µA", 1e6
        elif percentile_current >= 1e-9:
            return "nA", 1e9
        else:
            return "pA", 1e12

    def show_error_message(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(text)
        msg.setWindowTitle("Error")
        msg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    port_board = find_teensy_port()
    ex = CvMethod(port_board)
    ex.show()
    sys.exit(app.exec_())
