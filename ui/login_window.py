
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QDesktopWidget
from utils.api import login_api
from ui.styles import dark_style

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
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        # Connect to the database
        connection = sqlite3.connect("activity_monitor.db")  # Replace with your database name
        cursor = connection.cursor()

        # Check if the email and password already exist in the User table
        cursor.execute("SELECT email, password,employee_id FROM User WHERE email=? AND password=?", (email, password))
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
                self.accept()

            else:
                QMessageBox.warning(self, "Error", "Invalid email or password")

        # Close the database connection
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


# def login(self):
#     email = self.email_input.text()
#     password = self.password_input.text()
#
#     # Connect to the database
#     connection = sqlite3.connect("your_database.db")  # Replace with your database name
#     cursor = connection.cursor()
#
#     # Check if the email and password already exist in the User table
#     cursor.execute("SELECT email, password FROM User WHERE email=? AND password=?", (email, password))
#     result = cursor.fetchone()
#
#     if result:
#         # If email and password already exist, skip the login process
#         self.accept()
#     else:
#         # If they do not exist, proceed with the login API call
#         response = login_api(email, password)
#         if response.get("success"):
#             self.employee_id = response.get("employee_id")
#             # Store the employee ID in the database
#             self.store_employee_id(email, password, self.employee_id)
#             self.accept()
#         else:
#             QMessageBox.warning(self, "Error", "Invalid email or password")
#
#     # Close the database connection
#     connection.close()
#
#
#     def login(self):
#         email = self.email_input.text()
#         password = self.password_input.text()
#         response = login_api(email, password)
#         if response.get("success"):
#             self.employee_id = response.get("employee_id")
#             # Store the employee ID in the database
#             self.store_employee_id(email,password,self.employee_id)
#
#             self.accept()
#         else:
#             QMessageBox.warning(self, "Error", "Invalid email or password")