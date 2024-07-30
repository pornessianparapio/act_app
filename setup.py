from setuptools import setup, find_packages
import os
import sqlite3


# Function to create the local database
def create_local_database():
    db_path = os.path.join(os.path.expanduser("~"), "activity_monitor.db")
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

    # Create Activity table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            activity_name TEXT NOT NULL,
            app_name TEXT NOT NULL,
            no_of_times_app_opened INTEGER NOT NULL,
            ip_address TEXT NOT NULL,
            time_entry_id INTEGER NOT NULL,
            FOREIGN KEY (time_entry_id) REFERENCES Time_entry (id)
        )
    ''')

    # Create Time_entry table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Time_entry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_start_time TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            final_end_time TEXT NOT NULL,
            minutes INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


# Create the local database upon installation
create_local_database()

# Package setup
setup(
    name='ActivityMonitor',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "certifi==2024.7.4",
        "chardet==4.0.0",
        "charset-normalizer==3.3.2",
        "idna==2.10",
        "PyQt5==5.15.11",
        "PyQt5-Qt5==5.15.2",
        "PyQt5_sip==12.15.0",
        "python3-xlib==0.15",
        "pywin32==306",
        "requests==2.32.3",
        "setuptools==72.1.0",
        "urllib3==1.26.19",
        "WMI==1.5.1"
    ],
    entry_points={
        'console_scripts': [
            'activity_monitor=main:main'
        ]
    },
    author='Purvesh Bargat',
    author_email='bargatpurvesh@gmail.com',
    description='An activity monitoring application with a PyQt UI',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
)

