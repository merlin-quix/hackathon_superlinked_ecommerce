from quixstreams import Application
from quixstreams.kafka.configuration import ConnectionConfig
import os
import random
import time
import json
import uuid
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize the Quix Application with the connection configuration
app = Application()
topic = app.topic(os.getenv("raw_data_topic","raw_data"))
# for more help using QuixStreams see docs: https://quix.io/docs/quix-streams/introduction.html

def main():
    actions = ['view', 'hover', 'scroll', 'click']
    num_users = 100
    num_pages = 9
    # create a pre-configured Producer object.
    with app.get_producer() as producer:
        while True:
            current_time = int(time.time())
            record = {
                "timestamp": current_time,
                "user_id": f"user_{random.randint(1, num_users)}",
                "page_id": f"page_{random.randint(0, num_pages)}",
                "action": random.choice(actions)
            }
            json_data = json.dumps(record)

            # publish the data to the topic
            logger.info(f"Publishing row: {json_data}")
            producer.produce(
                topic=topic.name,
                key=str(uuid.uuid4()),
                value=json_data,
            )

            time.sleep(random.uniform(0.5, 10.5))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")