import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    finished = pyqtSignal(object)

    def __init__(self, inputs):
        super().__init__()
        self.inputs = inputs

    def run(self):
        # Your long-running code with array processing goes here
        result = [2 * x for x in self.inputs]
        if not self.isInterruptionRequested():
            self.finished.emit(result)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Stop Button Example')

        layout = QVBoxLayout()

        self.start_button = QPushButton('Start Process', self)
        self.start_button.clicked.connect(self.start_process)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop Process', self)
        self.stop_button.clicked.connect(self.stop_process)
        layout.addWidget(self.stop_button)
        self.stop_button.setEnabled(False)

        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

        self.worker_thread = None

    def start_process(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        inputs = [1, 2, 3, 4, 5]  # Replace with your actual input array
        self.worker_thread = WorkerThread(inputs)
        self.worker_thread.finished.connect(self.process_finished)
        self.worker_thread.start()

    def stop_process(self):
        if self.worker_thread:
            self.worker_thread.requestInterruption()
            self.worker_thread.wait()

    def process_finished(self, result):
        self.result_text.setPlainText(f"Result: {result}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
