import sys
from PyQt5.QtWidgets import QApplication, QDialog
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from init_db import initialize_db

if __name__ == "__main__":
    initialize_db()

    app = QApplication(sys.argv)

    try:
        login = LoginWindow()
        # print(login.exec_())
        # login.show()
        if login.exec_() == QDialog.Accepted:

            employee_id = login.get_employee_id()
            print(employee_id)
            window = MainWindow(employee_id)
            window.show()
    except Exception as e:
        print(f'couldnt open login window cuz: {e}')
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f'thrown after in the end {e}')
