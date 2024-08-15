import os
import datetime
import json

from flask import Flask, request, Response
from waitress import serve

from setup_logging import get_logger

from quixstreams.platforms.quix import QuixKafkaConfigsBuilder
from quixstreams.kafka import Producer

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

cfg_builder = QuixKafkaConfigsBuilder()
cfgs, topics, _ = cfg_builder.get_confluent_client_configs([os.environ["output"]])
producer = Producer(cfgs.pop("bootstrap.servers"), extra_config=cfgs)


logger = get_logger()

app = Flask(__name__)


@app.route("/data/", methods=['POST'])
def post_data():
    
    """
    Handles HTTP POST requests to `/data/`, receives JSON data, logs the request
    time and session ID, produces a message using a producer, and returns a
    successful response with CORS enabled.

    Returns:
        Response: 200 and has a header 'Access-Control-Allow-Origin' set to '*',
        indicating that the request was successful and CORS policy allows cross-origin
        resource sharing.

    """
    data = request.json

    print(data)

    logger.info(f"{str(datetime.datetime.utcnow())} posted.")
    
    producer.produce(topics[0], json.dumps(data), data["sessionId"])

    response = Response(status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=80)