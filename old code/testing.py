from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QLabel, QPushButton


class RadioExample(QWidget):
    def __init__(self):
        super().__init__()
        print("hello world")
        self.radio_buttons = []  # List to store radio buttons
        self.label = QLabel("Selected Radio Buttons:")
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.print_selected_radio_buttons)

        layout = QVBoxLayout()

        # Create and add radio buttons to the layout
        radio_labels = ["1k", "10k", "100k", "1M", "10M", "30M", "100M", "1G"]
        for label in radio_labels:
            radio_btn = QRadioButton(label)
            self.radio_buttons.append(radio_btn)
            layout.addWidget(radio_btn)

        layout.addWidget(self.start_button)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setWindowTitle("Radio Button Example")

    def print_selected_radio_buttons(self):
        selected_buttons = [radio_btn.text() for radio_btn in self.radio_buttons if radio_btn.isChecked()]
        self.label.setText(f"Selected Radio Buttons: {', '.join(selected_buttons)}")


app = QApplication([])
widget = RadioExample()
widget.show()
app.exec_()