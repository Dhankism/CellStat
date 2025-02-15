# PulseTab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt

class PulseTab(QWidget):
    def __init__(self,port):
        super().__init__()
        
        # Initialize the counter
        self.counter = 0

        layout = QVBoxLayout()

        # Label and Line Edit for Pulse Tab
        label = QLabel("Pulse Tab")
        line_edit = QLineEdit()
        
        # Counter Label and Button
        self.counter_label = QLabel(f"Counter: {self.counter}")
        self.counter_label.setAlignment(Qt.AlignCenter)
        increment_button = QPushButton("Increment Counter")
        increment_button.clicked.connect(self.increment_counter)

        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addWidget(self.counter_label)
        layout.addWidget(increment_button)
        
        self.setLayout(layout)

    def increment_counter(self):
        # Increment and update the counter
        self.counter += 1
        self.counter_label.setText(f"Counter: {self.counter}")
