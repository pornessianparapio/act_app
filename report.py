from init_db import db, TimeEntry, Activity, User
from datetime import datetime
import pandas as pd
import json
import os


import vercel_blob
#or
# import vercel_blob.blob_store
# or if you want to use an alias
import vercel_blob.blob_store as vb_store

def generate_report():
    # Querying the database
    db.connect()
    query = (Activity
             .select(Activity.activity_name, Activity.app_name, TimeEntry.minutes)
             .join(TimeEntry)
             )
    print(query)

    # Converting the query result to pandas DataFrame
    df = pd.DataFrame(list(query.dicts()))

    print(df)
    a=[]
    b=[]
    # 1. Top 5 app_name based on the minutes
    top_5_apps = df.groupby('app_name')['minutes'].sum().sort_values(ascending=False).head(5).to_dict().items()
    # print(top_5_apps.to_dict().items())
    for app_name,minutes in top_5_apps:
        a.append(app_name)
        b.append(minutes)

    print(a)
    print(b)

    # 2. Total Minutes Today
    total_minutes_today = df['minutes'].sum()

    # 3. Least used app_name
    least_used_app = df.groupby('app_name')['minutes'].sum().sort_values().head(1)

    # Creating the report
    report = {
        "Apps": a,
        "minutes": b

        # "Total Minutes Today": total_minutes_today,
        # "Least Used App": least_used_app.to_dict()
    }
    print(report)
    df2=pd.DataFrame(report)
    df2.to_csv('report.csv')

    return report


def list_all_blobs():
    blobs = vercel_blob.list({
        'limit': '5',
    })
def csv_to_binary_blob(file_path):
    with open(file_path, 'rb') as f:
        binary_blob = f.read()
    return binary_blob
def download_a_file_on_the_server(blob_url):
    vercel_blob.download_file(blob_url, 'path/to/directory/')

if __name__ == '__main__':
    # # report=generate_report()
    # generate_report()
    # report=csv_to_binary_blob('report.csv')
    # output={
    #     "Report":report
    # }
    # print(output)
    # print(os.environ)
    print(list_all_blobs())
    # vercel_blob.download_file(‘https://bzysnyfgxvzogl52.public.blob.vercel-storage.com/employee-data/app-CXrjlFbPXgsUGVc0nUxZNjsv6VKLv0.log’, ‘act_app’)




