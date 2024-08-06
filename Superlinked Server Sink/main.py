from quixstreams import Application

import os
import json
import redis

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

superlinked_host=os.environ['superlinked_host']
superlinked_port=os.environ['superlinked_port']

app = Application(consumer_group="superlinked-destination")

input_topic = app.topic(os.environ["input"])


def send_data_to_superlinked(data: dict) -> None:

    """
    Sends a JSON payload to a Superlinked API for event schema ingestion. It
    generates a random event ID and current timestamp, formats data from an input
    dictionary, and logs errors if the response status code is not 202.

    Args:
        data (dict): Expected to contain key-value pairs, specifically 'user',
            'product' and 'event_type'.

    """
    payload = {
            "user": data['user'],
            "product": data['product'],
            "event_type": data['event_type'],
            "id": generate_random_event_id(),  # Generate random event ID
            "created_at": generate_current_timestamp()  # Generate current timestamp
        }


    response = requests.post(
        f'http://{superlinked_host}:{superlinked_port}/api/v1/ingest/event_schema',
        headers={
            'Accept': '*/*',
            'Content-Type': 'application/json'
        },
        json=payload
    )

    print(f"Response for event {payload['id']}: {response.status_code} - {response.text}")

    # Check if response is not 202 and log to a file
    if response.status_code != 202:
        with open('error_log.txt', 'a') as log_file:
            log_file.write(f"Failed event {payload['id']}: {response.status_code} - {response.text}\n')


sdf = app.dataframe(input_topic)
sdf = sdf.update(send_data_to_superlinked)

if __name__ == "__main__":
    print("Starting application")
    app.run(sdf)