from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QMessageBox, QDialog
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer, QDateTime
from PyQt5 import uic
import logging
import sys
from monitoring.activity_monitor import ActivityMonitor
from ui.styles import dark_style
from .login_window import LoginWindow


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
        self.employee_details = employee_details
        uic.loadUi('ui/main_window.ui', self)  # Load the updated .ui file


        self.setWindowTitle("Activity Monitor")
        self.setStyleSheet(dark_style)
        self.center()

        self.monitor = ActivityMonitor(employee_id)
        self.monitoring_thread = None

        # Display employee details
        self.update_employee_details()

        # Set up and start the clock
        self.update_clock()
        self.start_clock()

        # Connect buttons to methods
        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.logout_button.clicked.connect(self.logout)

    def update_employee_details(self):
        # Update the labels with employee details
        self.Employee_Id_label.setText(f"Employee Id: {self.employee_details.get('userId', 'N/A')}")
        self.name_label.setText(f"Name: {self.employee_details.get('name', 'N/A')}")
        self.email_label.setText(f"Email: {self.employee_details.get('email', 'N/A')}")
        self.contact_label.setText(f"Contact: {self.employee_details.get('contact', 'N/A')}")
        self.address_label.setText(f"Address: {self.employee_details.get('address', 'N/A')}")
        self.joining_date_label.setText(f"Joining Date: {self.employee_details.get('joinDate', 'N/A')}")
        self.dob_label.setText(f"DOB: {self.employee_details.get('dob', 'N/A')}")

    def update_clock(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.clock_label.setText(f"Current Time: {current_time}")

    def start_clock(self):
        #update time clock 
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)  # Update every second

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

    def show_alert(self, message, title):
        QMessageBox.information(self, title, message)




