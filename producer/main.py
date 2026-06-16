import logging
import random
import time
from datetime import datetime, timedelta
from event_generator import EventGenerator
from event_writer import connect_db, write_events

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log"),
    ],
)

TOTAL_EVENTS = 100_000
DAYS = 7

HOURLY_WEIGHTS = [
    1, 1, 1, 1, 1, 1,    
    2, 3, 4,                  
    5, 5, 5, 4, 4, 5, 5, 5,  
    4, 7, 9, 10, 9, 7,       
    4,                        
]


def random_timestamp() -> datetime:
    hour = random.choices(range(24), weights=HOURLY_WEIGHTS, k=1)[0]
    days_ago = random.randint(0, DAYS - 1)
    base = datetime.now() - timedelta(days=days_ago)
    return base.replace(
        hour=hour,
        minute=random.randint(0, 59), 
        second=random.randint(0, 59),
        microsecond=0,
    )


def connect_db_with_retry(retries: int = 10, delay: int = 3):
    for i in range(retries):
        try:
            return connect_db()
        except Exception as e:
            logging.warning(f"DB not ready, retrying ({i + 1}/{retries}): {e}")
            time.sleep(delay)
    raise Exception("Failed to connect to DB after retries")


if __name__ == "__main__":
    generator = EventGenerator()
    conn = connect_db_with_retry()
    logging.info(f"Pipeline started: generating {TOTAL_EVENTS} events")

    try:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE events")
        conn.commit()
        logging.info("Table truncated")

        events = [generator.generate(timestamp=random_timestamp()) for _ in range(TOTAL_EVENTS)]
        write_events(conn, events)
        logging.info(f"Pipeline completed: {TOTAL_EVENTS} events written")
    finally:
        conn.close()