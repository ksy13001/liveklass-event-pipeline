import mysql.connector
import os
import logging
from collections import defaultdict
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE_DIR, "..", "charts")

EVENT_TYPE_COUNT_QUERY = """
    SELECT event_type, COUNT(*) as count
    FROM events
    GROUP BY event_type
    ORDER BY count DESC;
"""

HOURLY_EVENT_TREND_QUERY = """
    SELECT HOUR(timestamp) AS event_hour, event_type, COUNT(*)
    FROM events
    GROUP By event_hour, event_type
    ORDER BY event_hour, event_type DESC;
"""

def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def execute_query(conn, sql):
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        logging.error(e)
        raise


def plot_event_type_count(conn):
    rows = execute_query(conn, EVENT_TYPE_COUNT_QUERY)
    types = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    plt.figure(figsize=(10, 6))
    plt.bar(types, counts)
    plt.title("Event Count by Type")
    plt.xlabel("Event Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "event_type_count.png"))

    plt.close()


def plot_hourly_event_trend(conn):
    rows = execute_query(conn, HOURLY_EVENT_TREND_QUERY)

    data = defaultdict(dict)
    for hour, event_type, cnt in rows:
        data[event_type][hour] = cnt

    hours = list(range(24))
    plt.figure(figsize=(12, 6))

    for event_type, hour_counts in data.items():
        counts = [hour_counts.get(h, 0) for h in hours] 
        plt.plot(hours, counts, label=event_type, marker="o")

    plt.title("Hourly Event Trend")
    plt.xlabel("Hour")
    plt.ylabel("Count")
    plt.xticks(hours)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "hourly_trend.png"))
    plt.close()


if __name__ == "__main__":
    os.makedirs(CHARTS_DIR, exist_ok=True)
    conn = connect_db()
    try:
        plot_event_type_count(conn)
        plot_hourly_event_trend(conn)
    finally:
        conn.close()