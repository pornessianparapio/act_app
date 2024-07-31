# login_window.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QDesktopWidget
from utils.api import login_api
from ui.styles import dark_style

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
        response = login_api(email, password)
        if response.get("success"):
            self.employee_id = response.get("employee_id")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid email or password")

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
