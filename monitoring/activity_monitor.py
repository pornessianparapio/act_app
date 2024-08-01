from datetime import datetime
import sqlite3
import os
from monitoring.lib import get_current_window
from utils.helpers import get_ip_address
import threading

class ActivityMonitor:
    def __init__(self, employee_id):
        self.running = False
        self.employee_id = employee_id
        self.db_path = os.path.join("activity_monitor.db")
        self.conn = sqlite3.connect(self.db_path,check_same_thread=False)
        self.current_activity = None
        self.current_time_entry_id = None
        self.monitoring_thread = None

    def start_monitoring(self):
        cursor = self.conn.cursor()
        self.running = True

        while self.running:
            current_window = get_current_window()
            activity_name = current_window["title"]
            app_name = current_window["app"]
            ip_address = get_ip_address()

            # Check if the activity has changed
            if self.current_activity != (activity_name, app_name):
                end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print('Activity changed, handling new activity.')

                # End the previous time entry if it exists
                if self.current_time_entry_id:
                    cursor.execute('''
                        UPDATE TimeEntry
                        SET end_time = ?, final_end_time = ?, minutes = (julianday(?) - julianday(start_time)) * 1440
                        WHERE id = ?
                    ''', (end_time, end_time, end_time, self.current_time_entry_id))
                    self.conn.commit()

                # Start a new time entry
                start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''
                    INSERT INTO TimeEntry (first_start_time, start_time, end_time, final_end_time, minutes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (start_time, start_time, end_time, end_time, 0))
                self.current_time_entry_id = cursor.lastrowid
                self.conn.commit()

                # Check if the activity already exists
                cursor.execute('''
                    SELECT id, no_of_times_app_opened
                    FROM Activity
                    WHERE employee_id = ? AND activity_name = ? AND app_name = ?
                ''', (self.employee_id, activity_name, app_name))
                result = cursor.fetchone()

                if result:
                    activity_id, no_of_times_app_opened = result
                    # Increment the number of times the app has been opened
                    cursor.execute('''
                        UPDATE Activity
                        SET no_of_times_app_opened = ?
                        WHERE id = ?
                    ''', (no_of_times_app_opened + 1, activity_id))
                else:
                    # Insert new activity entry
                    cursor.execute('''
                        INSERT INTO Activity (employee_id, activity_name, app_name, no_of_times_app_opened, ip_address, TimeEntry_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (self.employee_id, activity_name, app_name, 1, ip_address, self.current_time_entry_id))

                self.conn.commit()
                self.current_activity = (activity_name, app_name)
                print('Activity recorded and committed.')
            else:
                print('Same app visited, no increment in count.')

    def start(self):
        self.monitoring_thread = threading.Thread(target=self.start_monitoring)
        print(self.monitoring_thread)

        self.monitoring_thread.start()

    def stop(self):
        self.running = False
        self.monitoring_thread.join()

        conn = sqlite3.connect(self.db_path,check_same_thread=False)
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