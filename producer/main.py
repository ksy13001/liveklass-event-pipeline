import logging
import random
import time
from event_generator import EventGenerator
from event_writer import connect_db, write_event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log"),
    ],
)

EVENT_INTERVAL_MIN = 0.05
EVENT_INTERVAL_MAX = 0.2


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
    logging.info("Pipeline started")

    try:
        while True:
            event = generator.generate()
            write_event(conn, event)
            time.sleep(random.uniform(EVENT_INTERVAL_MIN, EVENT_INTERVAL_MAX))
    except KeyboardInterrupt:
        logging.info("Pipeline stopped")
    finally:
        conn.close()