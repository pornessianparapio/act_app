
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QDesktopWidget
from utils.api import login_api
from ui.styles import dark_style
# from ui.main_window import MainWindow

import sqlite3
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.employee_id = None
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 200)
        self.setStyleSheet(dark_style)

        layout = QVBoxLayout()

        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        # Validation message label
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: red;")  # Set text color to red

        # self.email_input.setEchoMode(QLineEdit.Email)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.validation_label)
        self.email_input.textChanged.connect(self.validate_email)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        self.password_input.textChanged.connect(self.validate_password_length)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def validate_password_length(self):
        if len(self.password_input.text()) > 8:
            self.password_input.setText(self.password_input.text()[:8])
            # QMessageBox.warning(None, "Invalid Password", "Password cannot exceed 8 characters.")
            self.validation_label.setText("Password cannot exceed 8 characters.")

    def validate_email(self):
        email_text = self.email_input.text()
        if "@gmail.com" not in email_text:
            self.validation_label.setText("Email must contain '@gmail.com'.")
        else:
            self.validation_label.setText("")


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
            cursor.execute("SELECT email, password,employee_id FROM user WHERE email=? AND password=?", (email, password))
            result = cursor.fetchone()
            if result:
                # If email and password already exist, skip the login process
                self.employee_id = result[2]
                print(self.employee_id)
                self.accept()
            else:
                # If they do not exist, proceed with the login API call
                response = login_api(email, password)
                if response.get("success"):
                    self.employee_id = response.get("employee_id")
                    # Store the employee ID in the database
                    self.store_employee_id(email, password, self.employee_id)
                    # QMessageBox.information(self, "Login Successful", "Login successful.")
                    # self.show_alert("Login Successful.", "Login successful")
                    self.accept()
                else:
                    # QMessageBox.warning(self, "Error", "Invalid email or password")
                    self.show_alert("Invalid email or password", "Invalid credentials")

        except Exception as e:
            # QMessageBox.critical(self, "Unexpected Error", f"Unexpected error occurred: {str(e)}")
            self.show_alert(f"Unexpected error occurred: {str(e)}","Unexpected Error Occured")
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

    def showEvent(self, event):
        super().showEvent(event)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


