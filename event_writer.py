import mysql.connector
from dotenv import load_dotenv
import os
import logging

load_dotenv()

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


def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def write_event(conn, event: dict):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                INSERT_QUERY,
                (
                    event["event_id"],
                    event["event_type"],
                    event["user_id"],
                    event["order_id"],
                    event["lecture_id"],
                    event["amount"],
                    event["payment_method"],
                    event["timestamp"],
                ),
            )
        conn.commit()
    except Exception as e:
        logging.error(f"Error occurred while writing event: {e}")
        conn.rollback()
        raise