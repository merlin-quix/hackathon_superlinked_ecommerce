from quixstreams import Application

import os
import json
import redis


# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

r = redis.Redis(
    host=os.environ['redis_host'],
    port=int(int(os.environ['redis_port'])),
    password=os.environ['redis_password'],
    username=os.environ['redis_username'] if 'redis_username' in os.environ else None,
    decode_responses=True)

redis_key_prefix = os.environ['redis_key_prefix']

app = Application.Quix(consumer_group="redis-destination")

input_topic = app.topic(os.environ["input"])


def send_data_to_redis(value: dict) -> None:

    
    """
    Sends a JSON payload to an HTTP endpoint, checks if the response is successful
    (status code 202), and logs any errors to a file. If unsuccessful, it writes
    the error details to the log file.

    Args:
        value (dict): Not directly used within the function, indicating that it
            might be intended to store data prior to sending it to Redis. However,
            its purpose remains unclear without additional context.

    """
    response = requests.post(
        f'http://{superlinked_address}:8080/api/v1/ingest/event_schema',
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