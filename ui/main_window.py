from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, QCalendarWidget, QDesktopWidget, QMessageBox, QDialog, QGridLayout
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer, QDateTime
from PyQt5.QtGui import QPixmap
from monitoring.activity_monitor import ActivityMonitor  # Ensure this class is implemented correctly
from ui.styles import dark_style  # Ensure dark_style is defined
import logging
import sys
import traceback
from .login_window import LoginWindow


# Assuming you have an image for the profile picture
# PROFILE_PIC_PATH = '.\icons\login.png'  # put correct path

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    QMessageBox.critical(None, "An error occurred", "An unexpected error occurred. Please check the log file for details.")

sys.excepthook = handle_exception

class MonitoringThread(QThread):
    stop_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self._is_running = True
        self.stop_signal.connect(self.stop_monitoring)

    def run(self):
        try:
            self.monitor.start_monitoring(self._is_running)
        except Exception as e:
            logging.error("Error in monitoring thread", exc_info=True)
            self._is_running = False
            self.error_signal.emit(str(e))
            self.stop_signal.emit()

    @pyqtSlot()
    def stop_monitoring(self):
        self.monitor.stop()
        self._is_running = False

class MainWindow(QMainWindow):
    def __init__(self, employee_id, employee_details):
        super().__init__()
        self.employee_details = employee_details  # Store employee details
        self.setWindowTitle("Activity Monitor")
        self.setGeometry(100, 100, 800, 600)  # Adjusted window size
        self.setStyleSheet(dark_style)
        self.center()

        self.monitor = ActivityMonitor(employee_id)
        self.monitoring_thread = None

        main_layout = QVBoxLayout()

        # Top layout for clock and calendar
        top_layout = QHBoxLayout()

        # Clock
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("font-size: 18px;")
        top_layout.addWidget(self.clock_label)

        # Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setFixedSize(200, 150)
        top_layout.addWidget(self.calendar)

        # Adding employee details section
        details_layout = QGridLayout()

        # Profile Picture
        # self.profile_label = QLabel()
        # pixmap = QPixmap(PROFILE_PIC_PATH).scaled(100, 100)
        # self.profile_label.setPixmap(pixmap)
        # details_layout.addWidget(self.profile_label, 0, 0, 1, 2)

        # Employee Name
        self.name_label = QLabel(f"Name: {employee_details['name']}")
        details_layout.addWidget(self.name_label, 1, 0)

        # Employee Email
        self.email_label = QLabel(f"Email: {employee_details['email']}")
        details_layout.addWidget(self.email_label, 2, 0)

        # Employee Contact
        self.contact_label = QLabel(f"Contact: {employee_details['contact']}")
        details_layout.addWidget(self.contact_label, 3, 0)

        # Employee Address
        self.address_label = QLabel(f"Address: {employee_details['address']}")
        details_layout.addWidget(self.address_label, 4, 0)

        # Joining Date
        self.joining_date_label = QLabel(f"Joining Date: {employee_details['joinDate']}")
        details_layout.addWidget(self.joining_date_label, 5, 0)

        # Date of Birth
        self.dob_label = QLabel(f"Date of Birth: {employee_details['dob']}")
        details_layout.addWidget(self.dob_label, 6, 0)

        # Adding to main layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(details_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Monitoring")
        self.start_button.setStyleSheet("background-color: #5cb85c; color: white;")
        self.start_button.setFixedSize(150, 50)
        self.start_button.clicked.connect(self.start_monitoring)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.stop_button.setFixedSize(150, 50)
        self.stop_button.clicked.connect(self.stop_monitoring)
        button_layout.addWidget(self.stop_button)
        self.stop_button.setEnabled(False)

        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.logout_button.setFixedSize(150, 50)
        self.logout_button.clicked.connect(self.logout)
        button_layout.addWidget(self.logout_button)

        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Set up clock update
        self.update_clock()
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)  # Update every second

    def update_clock(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.clock_label.setText(f"Current Time: {current_time}")

    def start_monitoring(self):
        if not self.monitoring_thread or not self.monitoring_thread.isRunning():
            self.monitoring_thread = MonitoringThread(self.monitor)
            self.monitoring_thread.start()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.show_alert("Monitoring started successfully.", "Start Monitoring")

    def stop_monitoring(self):
        if self.monitoring_thread:
            self.monitoring_thread.stop_monitoring()
            self.monitoring_thread.quit()
            self.monitoring_thread = None
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.show_alert("Monitoring stopped successfully.", "Stop Monitoring")

    def logout(self):
        try:
            self.stop_monitoring()  # Stop monitoring before logging out
        except Exception as e:
            logging.error("Error during logout", exc_info=True)
        logging.info('Logging out...')
        self.show_alert("You've been logged out!", "Logged Out")
        self.close()  # Close the main window
        self.show_login_window()

    def show_login_window(self):
        login_window = LoginWindow()
        if login_window.exec_() == QDialog.Accepted:
            employee_id = login_window.get_employee_id()
            self.__init__(employee_id, self.employee_details)  # Reinitialize MainWindow with the new employee ID
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