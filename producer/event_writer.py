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
    error_code,
    error_page,
    timestamp)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def to_event_values(event: dict) -> tuple:
    return (
        event["event_id"],
        event["event_type"],
        event["user_id"],
        event["order_id"],
        event["lecture_id"],
        event["amount"],
        event["payment_method"],
        event.get("error_code"),
        event.get("error_page"),
        event["timestamp"],
    )


def write_events(conn, events: list[dict]):
    values_list = [to_event_values(event) for event in events]
    try:
        with conn.cursor() as cursor:
            cursor.executemany(INSERT_QUERY, values_list)
        conn.commit()
    except Exception as e:
        logging.error(f"batch_write_failed count={len(values_list)} error={e}")
        conn.rollback()
        raise
