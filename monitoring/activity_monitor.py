from datetime import datetime
import sqlite3
import os
import logging
from monitoring.lib import get_current_window
from utils.helpers import get_ip_address
from init_db import db, TimeEntry, Activity, User

# Set up logging
logging.basicConfig(filename='activity_monitor.log', level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')

class StopMonitoringException(Exception):
    pass

class ActivityMonitor:
    def __init__(self, employee_id):
        self.employee_id = employee_id
        self.current_activity = None
        self.current_time_entry_id = None

    def start_monitoring(self, running):
        db.connect()
        if running:
            try:
                while running:
                    current_window = get_current_window()
                    activity_name = current_window["title"]
                    app_name = current_window["app"]
                    ip_address = get_ip_address()

                    # Check if the activity has changed
                    if self.current_activity != (activity_name, app_name):
                        end_time = datetime.now()

                        # End the previous time entry if it exists
                        if self.current_time_entry_id:
                            time_entry = TimeEntry.get_by_id(self.current_time_entry_id)
                            time_entry.end_time = end_time
                            time_entry.final_end_time = end_time
                            time_entry.minutes = (end_time - time_entry.start_time).total_seconds() / 60
                            time_entry.save()

                        # Start a new time entry
                        start_time = datetime.now()
                        new_time_entry = TimeEntry.create(
                            first_start_time=start_time,
                            start_time=start_time,
                            end_time=end_time,
                            final_end_time=end_time,
                            minutes=0
                        )
                        self.current_time_entry_id = new_time_entry.id

                        # Check if the activity already exists
                        activity = Activity.get_or_none(
                            Activity.employee_id == self.employee_id,
                            Activity.activity_name == activity_name,
                            Activity.app_name == app_name
                        )

                        if activity:
                            # Increment the number of times the app has been opened
                            activity.no_of_times_app_opened += 1
                            activity.save()
                        else:
                            # Insert new activity entry
                            Activity.create(
                                employee_id=self.employee_id,
                                activity_name=activity_name,
                                app_name=app_name,
                                no_of_times_app_opened=1,
                                ip_address=ip_address,
                                time_entry=new_time_entry
                            )

                        self.current_activity = (activity_name, app_name)

            except Exception as e:
                logging.error("Error in start_monitoring", exc_info=True)
                raise StopMonitoringException from e
        else:
            try:
                if self.current_time_entry_id:
                    print('trying to stop')
                    end_time = datetime.now()
                    time_entry = TimeEntry.get_by_id(self.current_time_entry_id)
                    time_entry.end_time = end_time
                    time_entry.final_end_time = end_time
                    time_entry.minutes = (end_time - time_entry.start_time).total_seconds() / 60
                    print('saving')
                    time_entry.save()
                db.close()
            except Exception as e:
                logging.error("Error in stop", exc_info=True)

    def stop(self):
        running = False
        self.start_monitoring(running)