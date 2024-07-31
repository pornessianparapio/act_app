import sys
from PyQt5.QtWidgets import QApplication, QDialog
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = LoginWindow()
    if login.exec_() == QDialog.Accepted:
        employee_id = login.get_employee_id()
        print(employee_id)
        window = MainWindow(employee_id)
        window.show()

    sys.exit(app.exec_())
