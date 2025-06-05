# Main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QPushButton, QMessageBox
from CVTab import CVTab
from PULTab import PULTab

#from SWVTab import SWVTab
from ping import ping_by_vid

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # Ensure the QMainWindow superclass is initialized
        self.setWindowTitle("CellStat")
        self.setGeometry(100, 100, 1000, 1200)

        # Find all ports with matching Teensy VID
        self.port = str(ping_by_vid())

        # Create QTabWidget and 
        # set up tabs
        self.tabs = QTabWidget()
        self.cv_tab = CVTab(self.port)
        self.pulse_tab = PULTab(self.port)

        # Set custom tab names
        self.tabs.addTab(self.cv_tab, "CV")
        self.tabs.addTab(self.pulse_tab, "Pulse")

        # Set the central widget of the main window
        self.setCentralWidget(self.tabs)

         # Add button to update port
        self.update_port_button = QPushButton("Update Port")
        self.update_port_button.clicked.connect(self.update_port)
        self.tabs.setCornerWidget(self.update_port_button)
        if(self.port != 'None'):
            self.update_port_button.setText(f"Update Port (Current: {self.port})")
        else:
             self.update_port_button.setText("Update Port (No Device Found)")
        
    def update_port(self):
        if not self.cv_tab.is_process_running() and not self.swv_tab.is_process_running():
            self.port = str(ping_by_vid())

            self.cv_tab.update_port(self.port)
            self.pulse_tab.update_port(self.port)

            QMessageBox.information(self, "Port Updated", f"Port: {self.port}")
            self.update_port_button.setText(f"Update Port (Current: {self.port})")
        else:
            QMessageBox.warning(self, "Process Running", "Cannot update port while a process is running.")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
