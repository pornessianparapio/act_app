from datetime import datetime
import time
import sqlite3
from monitoring.lib import get_current_window
from utils.helpers import get_ip_address
import os

class ActivityMonitor:
    def __init__(self, employee_id):
        self.running = False
        self.employee_id = employee_id
        self.db_path = os.path.join( "activity_monitor.db")
        self.conn = sqlite3.connect("activity_monitor.db")
        # self.platform = sys.platform
        self.current_activity = None
        self.current_time_entry_id = None

    # def get_current_window(self):
    #     if self.platform.startswith("linux"):
    #         return linux.get_current_window()
    #     elif self.platform == "darwin":
    #         return macos.get_current_window(strategy="jxa")
    #     elif self.platform in ["win32", "cygwin"]:
    #         return windows.get_current_window()
    #     else:
    #         return {"app": "unknown", "title": "unknown"}

    def start_monitoring(self):
        cursor = self.conn.cursor()

        while True:
            current_window = get_current_window()
            activity_name = current_window["title"]
            app_name = current_window["app"]
            ip_address = get_ip_address()

            # Check if the activity has changed
            if self.current_activity != (activity_name, app_name):
                end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print('inside first if')

                if self.current_time_entry_id:
                    print('inside second if')
                    cursor.execute('''
                        UPDATE TimeEntry
                        SET end_time = ?, final_end_time = ?, minutes = (julianday(?) - julianday(start_time)) * 1440
                        WHERE id = ?
                    ''', (end_time, end_time, end_time, self.current_time_entry_id))
                    self.conn.commit()

                start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''
                    INSERT INTO TimeEntry (first_start_time, start_time, end_time, final_end_time, minutes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (start_time, start_time, end_time, end_time, 0))
                self.current_time_entry_id = cursor.lastrowid
                self.conn.commit()

                cursor.execute('''
                    INSERT INTO Activity (employee_id, activity_name, app_name, no_of_times_app_opened, ip_address, time_entry_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (self.employee_id, activity_name, app_name, 1, ip_address, self.current_time_entry_id))
                self.conn.commit()
                print('commited')

                self.current_activity = (activity_name, app_name)
            else:
                print('same app visited')
                cursor.execute('''
                    UPDATE Activity
                    SET no_of_times_app_opened = no_of_times_app_opened + 1
                    WHERE employee_id = ? AND activity_name = ? AND app_name = ?
                ''', (self.employee_id, activity_name, app_name))
                self.conn.commit()



    def stop(self):
        self.running = False

        conn = sqlite3.connect('activity_monitor.db')
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE TimeEntry
            SET end_time = datetime('now'), final_end_time = datetime('now'), minutes = (strftime('%s', 'now') - strftime('%s', start_time)) / 60
            WHERE employee_id = ? AND end_time IS NULL
        ''', (self.employee_id,))

        conn.commit()
        conn.close()