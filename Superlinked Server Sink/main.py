from quixstreams import Application

import os
import json
import redis

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

superlinked_host=os.environ['superlinked_host']
superlinked_port=os.environ['superlinked_port']

app = Application(consumer_group="redis-destination")

input_topic = app.topic(os.environ["input"])


def send_data_to_redis(value: dict) -> None:


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
sdf = sdf.update(send_data_to_redis)

if __name__ == "__main__":
    print("Starting application")
    app.run(sdf)