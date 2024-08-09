
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QDesktopWidget
from utils.api import login_api
from ui.styles import dark_style
from PyQt5 import uic
# from ui.main_window import MainWindow
import sqlite3
class LoginWindow(QDialog):


    def __init__(self):
        super().__init__()

        uic.loadUi('ui/login_window.ui', self)

        self.setWindowTitle("Login")

        self.setStyleSheet(dark_style)

        self.login_button.clicked.connect(self.login)

        self.employee_id = None
        self.employee_details=None



    # def validate_password_length(self):
    #         if len(self.password_input.text()) > 8:
    #             self.password_input.setText(self.password_input.text()[:8])
    #             # QMessageBox.warning(None, "Invalid Password", "Password cannot exceed 8 characters.")
    #             self.validation_label.setText("Password cannot exceed 8 characters.")
    #
    # def validate_email(self):
    #     email_text = self.email_input.text()
    #     if "@gmail.com" not in email_text:
    #         self.validation_label.setText("Email must contain '@gmail.com'.")
    #     else:
    #         self.validation_label.setText("")


    def show_alert(self, message, title="Alert"):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def login(self):
        try:
            email = self.email_input.text()
            password = self.password_input.text()

            # Connect to the database
            connection = sqlite3.connect("activity_monitor.db")  # Replace with your database name
            cursor = connection.cursor()

            # Check if the email and password already exist in the User table
            cursor.execute("SELECT email, password,employee_id FROM user WHERE email=? AND password=?",
                           (email, password))
            result = cursor.fetchone()
            if result:
                # If email and password already exist, skip the login process
                response = login_api(email, password)
                if response.get("success"):
                    self.employee_id = response.get("employee_id")
                    self.employee_details = response.get("employee_details")
                    self.accept()
                else:
                    self.show_alert("Invalid email or passwordd", "Invalid credentialss")
            else:
                # If they do not exist, proceed with the login API call
                response = login_api(email, password)
                if response.get("success"):
                    self.employee_id = response.get("employee_id")
                    self.employee_details = response.get("employee_details")
                    # Store the employee ID in the database
                    self.store_employee_id(email, password, self.employee_id)
                    self.accept()

                else:
                    self.show_alert("Invalid email or password", "Invalid credentials")

        except Exception as e:
            self.show_alert(f"Unexpected error occurred: {str(e)}", "Unexpected Error Occurred")

        finally:
            connection.close()

    def store_employee_id(self,email,password, employee_id):
        connection = sqlite3.connect("activity_monitor.db")  # Connect to the SQLite database
        cursor = connection.cursor()

        # Insert the employee ID into the employees table
        cursor.execute("INSERT INTO User (email,password,employee_id) VALUES (?,?,?)", (email,password,employee_id,))
        connection.commit()

        cursor.close()
        connection.close()

    def get_employee_id(self):
        return self.employee_id

    def get_employee_details(self):
        return self.employee_details
    def showEvent(self, event):
        super().showEvent(event)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


