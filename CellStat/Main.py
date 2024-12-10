# Main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from CVTab import CVTab
from PulseTab import PulseTab
from ping import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # Ensure the QMainWindow superclass is initialized
        global port
        self.setWindowTitle("CellStat")
        self.setGeometry(100, 100, 1000, 1200)

        # Find all ports with matching VID
        port= "com" + str(ping_by_vid())

        # Create QTabWidget and set up tabs
        self.tabs = QTabWidget()
        self.cv_tab = CVTab()
        self.pulse_tab = PulseTab()
        
        # Set custom tab names
        self.tabs.addTab(self.cv_tab, "CV")
        self.tabs.addTab(self.pulse_tab, "Pulse")
        
        # Set the central widget of the main window
        self.setCentralWidget(self.tabs)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
