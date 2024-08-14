import psycopg2
from urllib.parse import urlparse
def connect():
    conStr = "postgresql://neondb_owner:XYb3qAarseI6@ep-restless-credit-a59ac3mv.us-east-2.aws.neon.tech/neondb?sslmode=require"
    p = urlparse(conStr)
    print(p)

    pg_connection_dict = {
        'dbname': 'neondb',
        'user': p.username,
        'password': p.password,
        'port': p.port,
        'host': p.hostname
    }

    print(pg_connection_dict)
    con = psycopg2.connect(**pg_connection_dict)
    print(con)

if __name__ == "__main__":
    connect()


