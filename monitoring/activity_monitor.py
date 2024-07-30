import time
import sqlite3
from monitoring.lib import get_current_window
from utils.helpers import get_ip_address


class ActivityMonitor:
    def __init__(self, employee_id):
        self.running = False
        self.employee_id = employee_id

    def start(self):
        self.running = True
        ip_address = get_ip_address()
        conn = sqlite3.connect('activity_monitor.db')
        cursor = conn.cursor()

        while self.running:
            current_window = get_current_window()
            if current_window:
                cursor.execute('''
                    INSERT INTO TimeEntry (employee_id, first_start_time, start_time, end_time, final_end_time, minutes)
                    VALUES (?, datetime('now'), datetime('now'), NULL, NULL, 0)
                ''', (self.employee_id,))
                time_entry_id = cursor.lastrowid

                cursor.execute('''
                    INSERT INTO Activity (employee_id, activity_name, app_name, no_of_times_app_opened, ip_address, time_entry_id)
                    VALUES (?, ?, ?, 1, ?, ?)
                ''', (self.employee_id, current_window['title'], current_window['app'], ip_address, time_entry_id))

                conn.commit()
            time.sleep(5)

        conn.close()

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
