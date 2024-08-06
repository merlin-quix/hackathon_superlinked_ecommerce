from quixstreams import Application  # import the Quix Streams modules for interacting with Kafka:
# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# import additional modules as needed
import random
import os
import json
import random
import time
import requests
from collections import defaultdict
# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

# superlinked_address = "34.71.253.51"

# List of product IDs
product_ids = [
    "9", "20", "25", "36", "38", "39", "52", "56", "74", "83", "88", "94", "100", "101", "102", "109", "121", "122", "127", "133", "135", "138", "146", "152", "163", "171", "180", "181", "185", "187", "195", "198", "199", "218", "222", "226", "227", "233", "248", "251", "262", "275", "276", "279", "284", "288", "292", "305", "308", "310", "312", "315", "334", "336", "339", "369", "370", "386", "408", "416", "427", "442", "444", "462", "481", "488", "503", "511", "516", "520", "531", "535", "547", "561", "591", "618", "620", "625", "635", "658", "665", "668", "679", "684", "757", "766", "807", "814", "866", "891", "911", "912", "916", "962", "966", "995", "997", "1005", "1028", "1054", "1075", "1106", "1107", "1131", "1155", "1176", "1183", "1205", "1208", "1218", "1237", "1270", "1282", "1312", "1349", "1403", "1416", "1420", "1433", "1434", "1437", "1441", "1442", "1450", "1604", "1607", "1615", "1616", "1627", "1637", "1638", "1649", "1652", "1654", "1785"
]

# List of event types
event_types = ["clicked_on", "buy", "put_to_cart"]

# List of users
users = ["user_1", "user_2"]

# Function to generate a random event ID
def generate_random_event_id():
    return random.randint(100000, 999999)

# Function to generate the current timestamp as a Unix timestamp
def generate_current_timestamp():
    return int(time.time())

app = Application(consumer_group="data_source", auto_create_topics=True)  # create an Application

# define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

def main():
    """
    Read data from the hardcoded dataset and publish it to Kafka
    """

    event_history = defaultdict(list)  # To keep track of events for each user-product combo

    while True:
        user = random.choice(users)
        product = random.choice(product_ids)
        current_time = generate_current_timestamp()

        # Determine possible event types based on history for the same user-product combo
        possible_events = ["clicked_on"]
        history = event_history[(user, product)]

        if any(event["event_type"] == "clicked_on" for event in history):
            possible_events.append("put_to_cart")

        if any(event["event_type"] == "clicked_on" and (current_time - event["timestamp"]) <= 3600 for event in history):
            possible_events.append("buy")

        event_type = random.choice(possible_events)

        payload = {
            "user": user,
            "product": product,
            "event_type": event_type,
            "id": generate_random_event_id(),
            "created_at": current_time
        }

        # Append the event to the history for the same user-product combo
        event_history[(user, product)].append({
            "event_type": event_type,
            "timestamp": current_time
        })

        print(f"SENDING TO KAFKA: {payload}")
        # create a pre-configured Producer object.
        with app.get_producer() as producer:

            json_data = json.dumps(payload)  # convert the row to JSON

            # publish the data to the topic
            producer.produce(
                topic=topic.name,
                key=str(payload['id']),
                value=json_data,
            )

            # for more help using QuixStreams see docs:
            # https://quix.io/docs/quix-streams/introduction.html

            print("Row published")
            
        time.sleep(random.randint(1, 10))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")