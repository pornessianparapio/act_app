from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDesktopWidget, QDialog, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer, Qt, QRectF, QTime, QPointF
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygonF
import logging
import sys
from monitoring.activity_monitor import ActivityMonitor  # Ensure this class is implemented correctly
from ui.styles import dark_style  # Ensure dark_style is defined
from .login_window import LoginWindow

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    QMessageBox.critical(None, "An error occurred",
                         "An unexpected error occurred. Please check the log file for details.")


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


class AnalogClock(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def drawBackground(self, painter, rect):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(self.width() / 200.0, self.height() / 200.0)

        # Draw clock background
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(-100, -100, 200, 200)

        # Draw hour markers
        painter.setPen(QPen(Qt.white, 1))
        for i in range(0, 12):
            painter.drawLine(88, 0, 96, 0)
            painter.rotate(30.0)

        # Draw minute markers
        painter.setPen(QPen(Qt.white, 0.5))
        for i in range(0, 60):
            if (i % 5) != 0:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

        # Get current time
        time = QTime.currentTime()

        # Draw hour hand
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.white))
        painter.save()
        painter.rotate(30.0 * (time.hour() + time.minute() / 60.0))
        painter.drawPolygon(QPolygonF([QPointF(0, 7), QPointF(-7, 0), QPointF(0, -50), QPointF(7, 0)]))
        painter.restore()

        # Draw minute hand
        painter.setBrush(QBrush(Qt.white))
        painter.save()
        painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
        painter.drawPolygon(QPolygonF([QPointF(0, 7), QPointF(-7, 0), QPointF(0, -70), QPointF(7, 0)]))
        painter.restore()

        # Draw second hand
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.red))
        painter.save()
        painter.rotate(6.0 * time.second())
        painter.drawPolygon(QPolygonF([QPointF(0, 1), QPointF(-1, 0), QPointF(0, -90), QPointF(1, 0)]))
        painter.restore()


class MainWindow(QMainWindow):
    def __init__(self, employee_id):
        super().__init__()
        uic.loadUi('ui/main_window.ui', self)
        self.setWindowTitle("Activity Monitor")
        self.setStyleSheet(dark_style)
        self.center()

        self.monitor = ActivityMonitor(employee_id)
        self.monitoring_thread = None

        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.logout_button.clicked.connect(self.logout)

        # Add the analog clock to the graphics view
        self.clock = AnalogClock(self.graphicsView)
        self.graphicsView.setScene(self.clock.scene())

    def show_alert(self, message, title="Alert"):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

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
            # self.monitoring_thread.wait()
            self.monitoring_thread = None
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.show_alert("Monitoring stopped successfully.", "Stop Monitoring")

    def logout(self):
        try:
            self.stop_monitoring()  # Stop monitoring before logging out
        except Exception as e:
            logging.error("Error during logout", exc_info=True)
        self.show_alert("You've been logged out!", "Logged Out")
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
