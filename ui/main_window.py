from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget, QDesktopWidget
from monitoring.activity_monitor import ActivityMonitor
from ui.styles import dark_style

class MainWindow(QMainWindow):
    def __init__(self, employee_id):
        super().__init__()
        self.setWindowTitle("Activity Monitor")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet(dark_style)
        self.center()

        self.monitor = ActivityMonitor(employee_id)

        layout = QVBoxLayout()

        self.start_button = QPushButton("Start Monitoring")
        self.start_button.clicked.connect(self.start_monitoring)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.clicked.connect(self.stop_monitoring)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_monitoring(self):
        self.monitor.start_monitoring()

    def stop_monitoring(self):
        self.monitor.stop()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
