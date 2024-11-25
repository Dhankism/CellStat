import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QRadioButton, QPushButton, QButtonGroup
import sys


class PortSelectionDialog(QDialog):
    def __init__(self, ports):
        super().__init__()
        self.selected_port = None  # Variable to store the chosen port
        self.init_ui(ports)

    def init_ui(self, ports):
        self.setWindowTitle("Select a Port")
        layout = QVBoxLayout()

        # Add a label
        label = QLabel("Multiple devices detected. Select the port you wish to use:")
        layout.addWidget(label)

        # Add radio buttons for each port
        self.button_group = QButtonGroup(self)
        for port in ports:
            radio_button = QRadioButton(port)
            layout.addWidget(radio_button)
            self.button_group.addButton(radio_button)

        # Add OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.confirm_selection)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def confirm_selection(self):
        selected_button = self.button_group.checkedButton()
        if selected_button:
            self.selected_port = selected_button.text()  # Get the selected port
        self.accept()  # Close the dialog


def ping_by_vid(teensy_vid='16C0'):
    """
    Ping devices connected to the system by their VID.

    Args:
        teensy_vid (str): Vendor ID to match (default is Teensy's VID '16C0').

    Returns:
        str: The selected port if one or more devices are found, otherwise None.
    """
    # Find all ports with matching VID
    matching_ports = []
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.vid and f"{port.vid:04X}" == teensy_vid:
            matching_ports.append(port.device)

    if not matching_ports:
        print("No Teensy `devices detected.")
        return None

    # If only one matching port, select it automatically
    if len(matching_ports) == 1:
        print(f"Automatically selected port: {matching_ports[0]}")
        return matching_ports[0]

    # If multiple matching ports, show a selection dialog
    app = QApplication(sys.argv)
    dialog = PortSelectionDialog(matching_ports)
    if dialog.exec_() == QDialog.Accepted:
        selected_port = dialog.selected_port
        print(f"Selected port: {selected_port}")
        return selected_port

    return None


