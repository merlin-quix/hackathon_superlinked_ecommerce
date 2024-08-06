from quixstreams import Application
import random
import time
import os
import json

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

superlinked_host=os.environ['superlinked_host']
superlinked_port=os.environ['superlinked_port']

app = Application(consumer_group="superlinked-destination",auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])

# Function to generate random event ID
def generate_random_event_id():
    return f"event_{random.randint(1000, 9999)}"

# Function to generate current timestamp
def generate_current_timestamp():
    return int(time.time())

def send_data_to_superlinked(data: dict) -> None:

    """
    Sends a POST request to the Superlinked API with data from a dictionary. The
    payload is formatted as JSON and includes user, product, event type, a randomly
    generated ID, and current timestamp. The response status code and text are
    printed or logged in case of an error.

    Args:
        data (dict): Expected to contain the keys 'user', 'product', 'event_type'.
            The values for these keys are used to construct a payload dictionary
            before sending it to the Superlinked API.

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
            log_file.write(f"Failed event {payload['id']}: {response.status_code} - {response.text}\n")


sdf = app.dataframe(input_topic)
sdf = sdf.update(send_data_to_superlinked)

if __name__ == "__main__":
    print("Starting application")
    app.run(sdf)