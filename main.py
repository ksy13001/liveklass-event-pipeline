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


if __name__ == "__main__":
    generator = EventGenerator()
    conn = connect_db()
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