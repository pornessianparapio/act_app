# activity_monitor.py
from datetime import datetime
import time
import sqlite3
from monitoring.lib import get_current_window
from utils.helpers import get_ip_address
import os
import threading

class ActivityMonitor:
    def __init__(self, employee_id):
        self.running = False
        self.employee_id = employee_id
        self.db_path = os.path.join("activity_monitor.db")
        self.current_activity = None
        self.current_time_entry_id = None

    def start_monitoring(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        self.running = True

        while self.running:
            current_window = get_current_window()
            activity_name = current_window["title"]
            app_name = current_window["app"]
            ip_address = get_ip_address()

            # Check if the activity has changed
            if self.current_activity != (activity_name, app_name):
                end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if self.current_time_entry_id:
                    cursor.execute('''
                        UPDATE TimeEntry
                        SET end_time = ?, final_end_time = ?, minutes = (julianday(?) - julianday(start_time)) * 1440
                        WHERE id = ?
                    ''', (end_time, end_time, end_time, self.current_time_entry_id))
                    conn.commit()

                start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''
                    INSERT INTO TimeEntry (first_start_time, start_time, end_time, final_end_time, minutes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (start_time, start_time, end_time, end_time, 0))
                self.current_time_entry_id = cursor.lastrowid
                conn.commit()

                # Check if activity already exists
                cursor.execute('''
                    SELECT id FROM Activity
                    WHERE employee_id = ? AND activity_name = ? AND app_name = ?
                ''', (self.employee_id, activity_name, app_name))
                activity_row = cursor.fetchone()

                if activity_row:
                    cursor.execute('''
                        UPDATE Activity
                        SET no_of_times_app_opened = no_of_times_app_opened + 1,
                            ip_address = ?
                        WHERE id = ?
                    ''', (ip_address, activity_row[0]))
                else:
                    cursor.execute('''
                        INSERT INTO Activity (employee_id, activity_name, app_name, no_of_times_app_opened, ip_address, time_entry_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (self.employee_id, activity_name, app_name, 1, ip_address, self.current_time_entry_id))

                conn.commit()
                self.current_activity = (activity_name, app_name)
            else:
                cursor.execute('''
                    UPDATE Activity
                    SET no_of_times_app_opened = no_of_times_app_opened + 1
                    WHERE employee_id = ? AND activity_name = ? AND app_name = ?
                ''', (self.employee_id, activity_name, app_name))
                conn.commit()

            time.sleep(60)  # Adding sleep to reduce CPU usage

        conn.close()

    def start(self):
        self.monitoring_thread = threading.Thread(target=self.start_monitoring)

        self.monitoring_thread.start()


    def stop(self):
        self.running = False
        self.monitoring_thread.join()

        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.current_time_entry_id:
            cursor.execute('''
                UPDATE TimeEntry
                SET end_time = ?, final_end_time = ?, minutes = (julianday(?) - julianday(start_time)) * 1440
                WHERE id = ?
            ''', (end_time, end_time, end_time, self.current_time_entry_id))
            conn.commit()

        conn.close()
