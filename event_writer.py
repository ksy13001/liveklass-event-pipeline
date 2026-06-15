import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

INSERT_QUERY = """
INSERT INTO events (
    event_id, 
    event_type, 
    user_id, 
    order_id, 
    lecture_id, 
    amount, 
    payment_method, 
    timestamp)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

def write_event_to_db(event:dict):
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )
    
    cursor = conn.cursor()
    cursor.execute(INSERT_QUERY, (
        event["event_id"],
        event["event_type"],
        event["user_id"],
        event["order_id"],
        event["lecture_id"],
        event["amount"],
        event["payment_method"],
        event["timestamp"]
    ))
    
    conn.commit()
    cursor.close()
    conn.close()