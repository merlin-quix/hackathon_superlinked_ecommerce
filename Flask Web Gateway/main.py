import os
from flask import Flask, jsonify
from waitress import serve
import duckdb

from setup_logging import get_logger

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

logger = get_logger()

app = Flask(__name__)

# Replace with your MotherDuck connection string
connection_string = os.environ["MOTHERDUCK_CONNECTION_STRING"]

# Establish a connection to MotherDuck
conn = duckdb.connect(connection_string)

@app.route('/events', methods=['GET'])
def get_user_events():
    """
    Retrieves a list of user events from a database table named `user_events`,
    sorts them by `page_id`, and returns the results as JSON data. It logs the
    executed query for debugging purposes.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents an
        event returned from the database query and ordered by page_id in ascending
        order.

    """
    query = "SELECT * FROM user_events ORDER BY page_id ASC"

    logger.info(f"Running query: {query}")

    # Execute the query
    results = conn.execute(query).fetchdf()

    # Convert the result to a list of dictionaries
    results_list = results.to_dict(orient='records')

    return jsonify(results_list)

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=80)
