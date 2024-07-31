import os
import sqlite3


# Function to create the local database
def create_local_database():
    db_path = os.path.join("activity_monitor.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()


    # Create User table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            employee_id TEXT NOT NULL
        )
    ''')

    # Create Time_entry table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TimeEntry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_start_time TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            final_end_time TEXT NOT NULL,
            minutes INTEGER NOT NULL
        )
    ''')

    # Create Activity table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_name TEXT NOT NULL,
            employee_id TEXT NOT NULL,
            app_name TEXT NOT NULL,
            no_of_times_app_opened INTEGER NOT NULL,
            ip_address TEXT NOT NULL,
            TimeEntry_id INTEGER NOT NULL,
            FOREIGN KEY (TimeEntry_id) REFERENCES TimeEntry (id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_local_database()