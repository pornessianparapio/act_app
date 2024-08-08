from datetime import datetime
import logging
from monitoring.lib import get_current_window
from utils.helpers import get_ip_address
from init_db import db, TimeEntry, Activity, User
from queue import Queue
from collections import deque

# Set up logging
logging.basicConfig(filename='activity_monitor.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s:%(message)s')


class StopMonitoringException(Exception):
    pass


class Node:
    def __init__(self, activity):
        self.activity = activity
        self.next = None


class ActivityQueue:
    def __init__(self):
        self.front = None
        self.rear = None

    def enqueue(self, activity):
        new_node = Node(activity)
        if self.rear:
            self.rear.next = new_node
        self.rear = new_node
        if not self.front:
            self.front = new_node

    def dequeue(self):
        if not self.front:
            return None
        removed_node = self.front
        self.front = self.front.next
        if not self.front:
            self.rear = None
        return removed_node.activity

    def peek(self):
        return self.front.activity if self.front else None


class ActivityMonitor:
    def __init__(self, employee_id):
        self.employee_id = employee_id
        self.current_activity = None
        self.current_time_entry_id = None
        self.activity_queue = Queue()

    def start_monitoring(self, running):
        db.connect()
        print('start monitor')

        # **# Start monitoring loop**
        try:
            while running:
                current_window = get_current_window()
                activity_name = current_window["title"]
                app_name = current_window["app"]
                ip_address = get_ip_address()
                now = datetime.now()

                # Check if the activity has changed
                if self.current_activity != (activity_name, app_name):

                    if self.activity_queue.empty():
                        print('inside empty queue')
                        current_activity = Activity.get_or_none(
                            Activity.employee_id == self.employee_id,
                            Activity.activity_name == activity_name,
                            Activity.app_name == app_name
                        )

                        if current_activity:
                            current_activity.time_entry.start_time = now
                            current_activity.no_of_times_app_opened += 1
                            current_activity.time_entry.save()
                            current_activity.save()
                        else:
                            new_time_entry = TimeEntry.create(first_start_time=now, start_time=now)
                            Activity.create(
                                employee_id=self.employee_id,
                                activity_name=activity_name,
                                app_name=app_name,
                                no_of_times_app_opened=1,
                                ip_address=ip_address,
                                time_entry=new_time_entry
                            )

                        # **# Enqueue only new activities**
                        self.activity_queue.put(current_activity or Activity.get(
                            Activity.employee_id == self.employee_id,
                            Activity.activity_name == activity_name,
                            Activity.app_name == app_name
                        ))

                    if not self.activity_queue.empty():
                        print('inside not empty queue')
                        previous_activity = self.activity_queue.get()

                        if previous_activity:
                            previous_time_entry = previous_activity.time_entry
                            previous_time_entry.end_time = now
                            previous_time_entry.final_end_time = now
                            previous_time_entry.minutes += round(float(
                                (now - previous_time_entry.start_time).total_seconds() / 60), 2)
                            previous_time_entry.save()

                        current_activity = Activity.get_or_none(
                            Activity.employee_id == self.employee_id,
                            Activity.activity_name == activity_name,
                            Activity.app_name == app_name
                        )

                        if current_activity:
                            current_activity.time_entry.start_time = now
                            current_activity.no_of_times_app_opened += 1
                            current_activity.time_entry.save()
                            current_activity.save()
                        else:
                            new_time_entry = TimeEntry.create(first_start_time=now, start_time=now)
                            Activity.create(
                                employee_id=self.employee_id,
                                activity_name=activity_name,
                                app_name=app_name,
                                no_of_times_app_opened=1,
                                ip_address=ip_address,
                                time_entry=new_time_entry
                            )

                        # **# Enqueue only new activities**
                        self.activity_queue.put(current_activity or Activity.get(
                            Activity.employee_id == self.employee_id,
                            Activity.activity_name == activity_name,
                            Activity.app_name == app_name
                        ))

                    # **# Added a break condition to avoid an infinite loop**
                    if not running:
                        print('broken')
                        break

                    self.current_activity = (activity_name, app_name)

            else:
                try:
                    if self.current_time_entry_id:
                        end_time = datetime.now()

                        time_entry = TimeEntry.get_by_id(self.current_time_entry_id)
                        time_entry.end_time = end_time
                        time_entry.final_end_time = end_time
                        time_entry.minutes = (end_time - time_entry.start_time).total_seconds() / 60
                        time_entry.save()
                    db.close()
                    print('closed')

                except Exception as e:
                    logging.error("Error in stop", exc_info=True)

        except Exception as e:
            logging.error("Error in start_monitoring", exc_info=True)
            raise StopMonitoringException from e

    def stop(self):
        running = False
        self.start_monitoring(running)
