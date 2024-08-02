# main_window.py
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget, QDesktopWidget, QMessageBox, QDialog
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from monitoring.activity_monitor import ActivityMonitor  # Ensure this class is implemented correctly
from ui.styles import dark_style  # Ensure dark_style is defined
import logging
from .login_window import LoginWindow

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

class MonitoringThread(QThread):
    stop_signal = pyqtSignal()

    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self._is_running = True
        self.stop_signal.connect(self.stop)

    def run(self):
        try:
            self.monitor.start_monitoring()
        except Exception as e:
            logging.error("Error in monitoring thread", exc_info=True)
            self._is_running = False
            self.stop_signal.emit()

    @pyqtSlot()
    def stop(self):
        self.monitor.stop()
        self._is_running = False

    def stop_monitoring(self):
        self.stop_signal.emit()

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
        self.start_button.setStyleSheet("background-color: #5cb85c; color: white;")
        self.start_button.setFixedSize(150, 50)
        self.start_button.clicked.connect(self.start_monitoring)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.stop_button.setFixedSize(150, 50)
        self.stop_button.clicked.connect(self.stop_monitoring)
        layout.addWidget(self.stop_button)

        self.stop_button.setEnabled(False)

        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.logout_button.setFixedSize(150, 50)
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.logout_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_alert(self, message, title="Alert"):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def start_monitoring(self):
        if not self.monitoring_thread:
            self.monitoring_thread = MonitoringThread(self.monitor)
            self.monitoring_thread.start()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.show_alert("Monitoring started successfully.", "Start Monitoring")

    def stop_monitoring(self):
        if self.monitoring_thread:
            self.monitoring_thread.stop_monitoring()
            self.monitoring_thread.quit()
            self.monitoring_thread.wait()
            self.monitoring_thread = None
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.show_alert("Monitoring stopped successfully.", "Stop Monitoring")

    def logout(self):
        try:
            self.stop_monitoring()  # Stop monitoring before logging out
        except Exception as e:
            print(f'thrown while stop monitoring {e}')
        print('Logging out...')
        self.show_alert("You've been logged out!.", "Logged Out")
        self.close()  # Close the main window
        self.show_login_window()


    def show_login_window(self):
        login_window = LoginWindow()
        if login_window.exec_() == QDialog.Accepted:
            employee_id = login_window.get_employee_id()

            self.__init__(employee_id)  # Reinitialize MainWindow with the new employee ID
            self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        if self.monitoring_thread and self.monitoring_thread.isRunning():
            self.stop_monitoring()
        event.accept()
