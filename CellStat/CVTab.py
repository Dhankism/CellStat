# CVTab.py
from multiprocessing import Process
from operator import index
import matplotlib.pyplot as plt
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


from ping import *
from cailbration import *

CodeRunningFlag=False
PortNumber=3
BAUD_RATE = 115200
TIMEOUT = 3

class CVTab(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QGridLayout()

        # Label and Line Edit for CV Tab
        i = QLabel("CV Tab")

        #PortNumber=ping_by_vid()
        self.PortNumber=3
        self.L_PortNum = QLabel("Port number: " + str(self.PortNumber))
        self.Ping_button = QPushButton("Reset")


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

        layout.addWidget(self.L_PortNum,0,0)
        layout.addWidget(self.Ping_button,0,1)
        layout.addWidget(self.L_StartVoltage,1,0)
        layout.addWidget(self.I_StartVoltage,1,1)
        layout.addWidget(self.L_FirstVoltage,2,0)
        layout.addWidget(self.I_FirstVoltage,2,1)
        layout.addWidget(self.L_SecondVoltage,3,0)
        layout.addWidget(self.I_SecondVoltage,3,1)
        
        layout.addWidget(self.L_NumCycles,0,2)
        layout.addWidget(self.I_NumCycles,0,3)
        layout.addWidget(self.L_ScanRate,1,2)
        layout.addWidget(self.I_ScanRate,1,3)
        layout.addWidget(self.L_CurrentRange,2,2)
        layout.addLayout(self.RangeList,2,3)
        layout.addWidget(self.L_CapRange,3,2)
        layout.addLayout(self.CapList,3,3)

        layout.addWidget(self.L_FileName,4,0)
        layout.addWidget(self.I_FileName,4,1,1,4)

        layout.addWidget(self.StopButton,5,0)
        layout.addWidget(self.StartButton,5,1,1,1)
        layout.addWidget(self.SaveButton,5,3)
       
       # Creating the canvas for plotting and the toolbar
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot(111)
       
        layout.addWidget(self.toolbar,6,0,1,2)
        layout.addWidget(self.canvas,7,0,5,5)

        self.setLayout(layout)


    # Function to run the CV process and to check the inputs
    def Run_CMD(self):


        i= [i for i, radio_btn in enumerate(self.RangeGroup.buttons()) if radio_btn.isChecked()]


        if not i[0]:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Please select a current range.")
            error_dialog.setWindowTitle("Input Error")
            error_dialog.exec_()
            return
        RITA=int(ResistorValues[i[0]])
        print(RITA)


        cycnum = int(self.I_NumCycles.text())
        startvolt = float(self.I_StartVoltage.text())
        firstvolt = float(self.I_FirstVoltage.text())
        secondvolt = float(self.I_SecondVoltage.text())
        scanrate = float(self.I_ScanRate.text())
        resistorval = float(RITA)
        filename = self.I_FileName.text()

   
        if cycnum <= 0 or cycnum > 100:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Number of cycles must be between 1 and 100")
            error_dialog.setWindowTitle("Input Error")
            error_dialog.exec_()
            return

        if startvolt < -2.5 or startvolt > 2.5 or firstvolt < -2.5 or firstvolt > 2.5 or secondvolt < -2.5 or secondvolt > 2.5:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Start potential must be between -2.5 and +2.5 V")
            error_dialog.setWindowTitle("Input Error")
            error_dialog.exec_()
            return

        if scanrate <= 0.00001 or scanrate > 100:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Scan rate must be between 0.00001 and 100 V/s")
            error_dialog.setWindowTitle("Input Error")
            error_dialog.exec_()
            return
        
        # Check if current range and capacitor range buttons are selected
        current_range_selected = self.current_range_button_group.checkedButton()
        capacitor_range_selected = self.capacitor_range_button_group.checkedButton()


        if not current_range_selected:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Please select a current range.")
            error_dialog.setWindowTitle("Input Error")
            error_dialog.exec_()
            return

        if not capacitor_range_selected:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Please select a capacitor range.")
            error_dialog.setWindowTitle("Input Error")
            error_dialog.exec_()
            return


        print("Running CV with the following parameters:")
        print(f"Number of cycles: {cycnum}")
        print(f"Start potential: {startvolt}")
        print(f"First inversion potential: {firstvolt}")
        print(f"Second inversion potential: {secondvolt}")
        print(f"Scan rate: {scanrate}")
        print(f"Resistor value: {resistorval}")
        print(f"Filename: {filename}")

        # Only start if there's no active process
        if self.process is None or not self.process.is_alive():
            self.process = Process(target=execute_CV)
            self.process.start()

    def Stop_CMD(self):
        # Terminate the process if it's running
        if self.process is not None and self.process.is_alive():
            self.process.terminate()
            self.process.join()  # Ensure the process has fully terminated
            self.process = None  # Reset the process reference
            print("Task terminated")


def execute_CV( ):
    
    for i in range(20):
        time.sleep(1)  # Simulating a long task (20 seconds in total)
        print(f"Running... {i + 1} seconds")  # This will show in the console
    print("Task completed")



