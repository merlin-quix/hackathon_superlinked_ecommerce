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

### WARPSTREAM CONNECTION
# Define your SASL configuration
connection = ConnectionConfig(
     bootstrap_servers=os.environ["bootstrap_server"],
     security_protocol="SASL_SSL",
     sasl_mechanism="PLAIN",  # or any other supported mechanism
     sasl_username=os.environ["sasl_username"],
     sasl_password=os.environ["sasl_password"]
 )

# Initialize the Quix Application with the connection configuration
app = Application(broker_address=connection)
topic = app.topic(os.getenv("raw_data_topic","raw_data"))
# for more help using QuixStreams see docs: https://quix.io/docs/quix-streams/introduction.html

def main():
    """
    Publishes random records to a Kafka topic with producer. Each record contains
    timestamp, user_id, page_id and an action (view, hover, scroll or click)
    simulated by a random choice from a list. The records are published at a random
    interval between 0.5 to 1.5 seconds.

    """
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

            time.sleep(random.uniform(0.5, 1.5))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")