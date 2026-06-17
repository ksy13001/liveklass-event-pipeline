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

ERROR_CODE_COUNT_QUERY = """
    SELECT error_code, COUNT(*) as count
    FROM events
    WHERE event_type = 'error'
    GROUP BY error_code
    ORDER BY count DESC;
"""

DAILY_EVENT_TREND_QUERY = """
    SELECT DATE(timestamp) AS date, event_type, COUNT(*)
    FROM events
    GROUP BY date, event_type
    ORDER BY date, event_type;
"""

DAILY_REVENUE_QUERY = """
    SELECT
        DATE(timestamp) AS date,
        SUM(CASE WHEN event_type = 'purchase_complete' THEN amount ELSE 0 END) AS revenue,
        SUM(CASE WHEN event_type = 'purchase_cancel'  THEN amount ELSE 0 END) AS refund,
        SUM(CASE WHEN event_type = 'purchase_complete' THEN amount ELSE 0 END) -
        SUM(CASE WHEN event_type = 'purchase_cancel'  THEN amount ELSE 0 END) AS net_revenue
    FROM events
    GROUP BY date
    ORDER BY date;
"""

EVENT_TYPE_COLORS = {
    "page_view":         "#4C72B0",
    "purchase_complete": "#55A868",
    "purchase_cancel":   "#DD8452",
    "error":             "#C44E52",
}


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
    total = sum(counts)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(types, counts, color=[EVENT_TYPE_COLORS[t] for t in types])
    plt.bar_label(bars, labels=[f"{c / total * 100:.1f}%" for c in counts], padding=4)
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
        plt.plot(hours, counts, label=event_type, marker="o", markerfacecolor="none", color=EVENT_TYPE_COLORS.get(event_type))

    plt.title("Hourly Event Trend")
    plt.xlabel("Hour")
    plt.ylabel("Count")
    plt.xticks(hours)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "hourly_trend.png"))
    plt.close()


def plot_error_code_count(conn):
    rows = execute_query(conn, ERROR_CODE_COUNT_QUERY)
    codes = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=codes, autopct="%1.1f%%", startangle=90,
            textprops={"fontsize": 14})
    plt.title("Error Distribution by Code", fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "error_code_distribution.png"))
    plt.close()


def plot_daily_event_trend(conn):
    rows = execute_query(conn, DAILY_EVENT_TREND_QUERY)

    data = defaultdict(dict)
    for date, event_type, cnt in rows:
        data[event_type][date] = cnt

    dates = sorted({r[0] for r in rows})
    plt.figure(figsize=(12, 6))

    for event_type, date_counts in data.items():
        counts = [date_counts.get(d, 0) for d in dates]
        plt.plot(dates, counts, label=event_type, marker="o", markerfacecolor="none", color=EVENT_TYPE_COLORS.get(event_type))

    plt.title("Daily Event Trend")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "daily_trend.png"))
    plt.close()


def plot_daily_revenue(conn):
    rows = execute_query(conn, DAILY_REVENUE_QUERY)
    dates = [r[0] for r in rows]
    revenue = [int(r[1]) // 10000 for r in rows]
    refund = [int(r[2]) // 10000 for r in rows]
    net_revenue = [int(r[3]) // 10000 for r in rows]

    plt.figure(figsize=(12, 6))
    plt.plot(dates, revenue, label="Revenue", marker="o", markerfacecolor="none", color="#4C72B0")
    plt.plot(dates, refund, label="Refund", marker="o", markerfacecolor="none", color="#C44E52")
    plt.plot(dates, net_revenue, label="Net Revenue", marker="o", markerfacecolor="none", color="#55A868")
    plt.title("Daily Revenue")
    plt.xlabel("Date")
    plt.ylabel("Amount (10,000 KRW)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "daily_revenue.png"))
    plt.close()


if __name__ == "__main__":
    os.makedirs(CHARTS_DIR, exist_ok=True)
    conn = connect_db()
    try:
        plot_event_type_count(conn)
        plot_hourly_event_trend(conn)
        plot_error_code_count(conn)
        plot_daily_event_trend(conn)
        plot_daily_revenue(conn)
    finally:
        conn.close()