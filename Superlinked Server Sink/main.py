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
    Posts a JSON payload to a specified URL, verifying the response status code
    is 202. If not, it writes an error log. The function prints success or failure
    messages along with the response details.

    Args:
        value (dict): Required by the function. Its content and usage are not
            specified within this code snippet, but it is expected to be used as
            a payload for sending data to Redis through a POST request.

    """
    response = requests.post(
        f'http://{superlinked_host}:{8080}/api/v1/ingest/event_schema',
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