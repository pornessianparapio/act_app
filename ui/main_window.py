# main_window.py
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget, QDesktopWidget
from PyQt5.QtCore import QThread, pyqtSignal
from monitoring.activity_monitor import ActivityMonitor
from ui.styles import dark_style

class MonitoringThread(QThread):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor

    def run(self):
        self.monitor.start_monitoring()

class MainWindow(QMainWindow):
    def __init__(self, employee_id):
        super().__init__()
        self.setWindowTitle("Activity Monitor")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet(dark_style)
        self.center()

        self.monitor = ActivityMonitor(employee_id)
        self.monitoring_thread = None

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
        if not self.monitoring_thread:
            self.monitoring_thread = MonitoringThread(self.monitor)
            print(f'thread start {self.monitoring_thread}')
            self.monitoring_thread.start()

    def stop_monitoring(self):
        if self.monitoring_thread:
            self.monitor.stop()
            self.monitoring_thread.quit()
            self.monitoring_thread.wait()
            self.monitoring_thread = None

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())