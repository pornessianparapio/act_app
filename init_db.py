from peewee import *

db = SqliteDatabase('activity_monitor.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    email = CharField(unique=True)
    password = CharField()
    employee_id = CharField(unique=True)

class TimeEntry(BaseModel):
    first_start_time = DateTimeField()
    start_time = DateTimeField()
    end_time = DateTimeField()
    final_end_time = DateTimeField()
    minutes = IntegerField()
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
