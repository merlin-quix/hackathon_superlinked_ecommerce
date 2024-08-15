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

def to_duckdb(conn, msg):
    """
    Collects and stores statistics for a given repository by inserting referral
    records into a DuckDB table, overwriting existing entries if necessary, and
    logs events during the process. It also creates the table if it does not exist.

    Args:
        conn (sqlite3.Connection): Used to establish a connection to a SQLite
            database, providing access for executing SQL queries and storing data.
        msg (Dict[str, Any]): Assumed to contain two key-value pairs: "repo" which
            corresponds to the name of the source repository and "day_recorded"
            which corresponds to the timestamp for recorded day, as well as a list
            of referrals in the "referrals" key.

    """
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
                    repo VARCHAR,
                    referrer VARCHAR,
                    count INTEGER,
                    uniques INTEGER,
                    day TIMESTAMP,
                    UNIQUE(repo, referrer, day)
                );
            ''')

        for record in msg["referrals"]:
            conn.execute(f'''
                INSERT INTO {user_events_table} (repo, referrer, count, uniques, day) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (repo, referrer, day) # Need to overwrite rather than insert if same combo of date-repo-referrer already exists
                DO UPDATE SET count = excluded.count, uniques = excluded.uniques;
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
