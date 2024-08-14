from peewee import *
import logging


logging.basicConfig(filename='db.log', level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')
db = SqliteDatabase('activity_monitor.db')


class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    email = CharField(unique=True)
    password = CharField()
    employee_id = CharField(unique=True)

class TimeEntry(BaseModel):
    first_start_time = DateTimeField(default=0)
    start_time = DateTimeField(default=0)
    end_time = DateTimeField(default=0)
    final_end_time = DateTimeField(default=0)
    minutes = FloatField(default=0)
    # user = ForeignKeyField(User, backref='time_entries')

class Activity(BaseModel):
    employee_id = CharField()
    activity_name = CharField()
    app_name = CharField()
    no_of_times_app_opened = IntegerField(default=0)
    ip_address = CharField()
    time_entry = ForeignKeyField(TimeEntry, backref='activities')

def initialize_db():
    with db:
        db.create_tables([User, Activity, TimeEntry])

if __name__ == '__main__':
    initialize_db()
