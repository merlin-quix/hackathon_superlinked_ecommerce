from quixstreams import Application
import duckdb
import os
import logging
import datetime
from dotenv import load_dotenv
load_dotenv()

mdtoken = os.environ['MOTHERDUCK_TOKEN']
mddatabase = os.environ['MOTHERDUCK_DATABASE']
# initiate the MotherDuck connection through a service token through
con = duckdb.connect(f'md:{mddatabase}?motherduck_token={mdtoken}')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_events_table = "user_events"

#      payload = {
#           "user": user,
#           "product": product,
#           "event_type": event_type,
#           "id": generate_random_event_id(),
#           "created_at": current_time
#       }

def to_duckdb(conn, msg):
    try:
        sourcerepo = msg["repo"]
        reportedtime = msg["day_recorded"]
        logger.info(f"####### Collecting stats for repo {sourcerepo}")

        # Check if the referrals table exists and create it if not
        table_exists = conn.execute(
            f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{user_events_table}')").fetchone()[0]
        if not table_exists:

            conn.execute(f'''
                CREATE TABLE {user_events_table} (
                    user VARCHAR,
                    product VARCHAR,
                    event_type INTEGER,
                    id INTEGER,
                    created_at TIMESTAMP,
                );
            ''')

        for record in msg["referrals"]:
            conn.execute(f'''
                INSERT INTO {user_events_table} (user, product, event_type, uniques, day) VALUES (?, ?, ?, ?, ?)
                ''', (sourcerepo, record['referrer'], record['count'], record['uniques'], reportedtime))
            logger.info(f"Wrote referral record: {record}")

       

    except Exception as e:
        logger.info(f"{str(datetime.datetime.utcnow())}: Write failed")
        logger.info(e)

# Define your application and settings
app = Application(
    consumer_group=os.environ['CONSUMER_GROUP_NAME'],
    auto_offset_reset="earliest",
)

# Define an input topic with JSON deserializer
input_topic = app.topic(os.environ['input'], value_deserializer="json")

# Initialize a streaming dataframe based on the stream of messages from the input topic:
sdf = app.dataframe(topic=input_topic)
sdf = sdf.update(lambda val: print(f"Received update: {val}"))

# Trigger the write function for any new messages(rows) in the SDF
sdf = sdf.update(lambda val: to_duckdb(con, val), stateful=False)

app.run(sdf)
