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
mdtoken = os.environ['MOTHERDUCK_TOKEN']
mddatabase = os.environ['MOTHERDUCK_DATABASE']

# initiate the MotherDuck connection through a service token through
conn = duckdb.connect(f'md:{mddatabase}?motherduck_token={mdtoken}')

@app.route('/events', methods=['GET'])
def get_user_events():
    query = "SELECT * FROM user_events ORDER BY page_id ASC"

    logger.info(f"Running query: {query}")

    # Execute the query
    results = conn.execute(query).fetchdf()

    # Convert the result to a list of dictionaries
    results_list = results.to_dict(orient='records')

    return jsonify(results_list)

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=80)
