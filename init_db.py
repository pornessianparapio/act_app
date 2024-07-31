import os
import sqlite3


def initialize_db():
    if not os.path.exists('activity_monitor.db'):
        conn = sqlite3.connect('activity_monitor.db')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS User (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email TEXT,
                            password TEXT,
                            employee_id TEXT)''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TimeEntry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_start_time TEXT,
                start_time TEXT,
                end_time TEXT,
                final_end_time TEXT,
                minutes REAL
            )
            ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT,
                activity_name TEXT,
                app_name TEXT,
                no_of_times_app_opened INTEGER,
                ip_address TEXT,
                time_entry_id INTEGER,
                UNIQUE(employee_id, activity_name, app_name) -- Ensure no duplicate activities
            )
            ''')

        conn.commit()
        conn.close()

if __name__ == "__main__":
    initialize_db()