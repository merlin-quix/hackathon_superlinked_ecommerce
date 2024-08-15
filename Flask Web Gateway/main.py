import os
from flask import Flask, jsonify
from waitress import serve
import duckdb
import logging

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Replace with your MotherDuck connection string
mdtoken = os.environ['MOTHERDUCK_TOKEN']
mddatabase = os.environ['MOTHERDUCK_DATABASE']

# Establish a connection to MotherDuck
conn = duckdb.connect(f'md:{mddatabase}?motherduck_token={mdtoken}')

@app.route('/events', methods=['GET'])
def get_user_events():
    """
    Retrieves a list of user events from a database table, ordered by page ID in
    ascending order, and returns the results as JSON data.

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents an
        event returned from the query result and its corresponding columns from
        the database.

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
