import os
import json
# import requests
from google.cloud import secretmanager
from flask import Flask
from pymongo import MongoClient
# from datetime import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('flask')

def access_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    """
    Access the secret from Google Cloud Secret Manager
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.debug(f"Error accessing secret: {e}")
        # app.logger.debug(f"Error accessing secret: {e}")
        raise


def setup_mongodb_connection():
    try:
        project_id = "mashcantas-dev"
        secret_id = os.environ.get("SECRET_ID", "mainMongoUri_dev")  # Default to your secret name
        mongo_secret = access_secret(project_id, secret_id)

        # Parse the JSON string into a dictionary
        secret_dict = json.loads(mongo_secret)
        mongo_uri = secret_dict["MONGO_URI"]


        # Create MongoDB client
        client = MongoClient(mongo_uri)

        # Test the connection
        client.admin.command('ping')
        logger.debug("Successfully connected to MongoDB!")
        # app.logger.debug("Successfully connected to MongoDB!")

        return client
    except Exception as e:
        logger.debug(f"Failed to connect to MongoDB: {e}")
        # app.logger.debug(f"Failed to connect to MongoDB: {e}")
        raise


# Initialize MongoDB connection when app starts
try:
    mongo_client = setup_mongodb_connection()
    db = mongo_client["mashcantas-dev-db-cluster"]  # Replace with your database name
    collection = db["dev_tests_v01"]  # Replace with your collection name
except Exception as e:
    logger.debug(f"Failed to initialize MongoDB: {e}")
    # app.logger.debug(f"Failed to initialize MongoDB: {e}")
    raise


# Example write route: writes the current timestamp
# @app.route('/api/flask/write', methods=['POST'])
# def write_timestamp():
#     now = datetime.datetime.now()
#     doc = {"timestamp": now}
#     try:
#         logger.debug("doc is: ", doc)
#         app.logger.debug("doc is: ", doc)
#         result = collection.insert_one(doc)
#         logger.debug("insert one result: ", result)
#         app.logger.debug("insert one result: ", result)
#         return jsonify({"message": "Timestamp written", "timestamp": now.isoformat()}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
#
# # Example read route: reads the last written timestamp
# @app.route('/api/flask/read', methods=['GET'])
# def read_last_timestamp():
#     try:
#         doc = collection.find().sort("_id", -1).limit(1)
#         last_doc = next(doc, None)
#         if last_doc:
#             return jsonify({"last_timestamp": last_doc["timestamp"].isoformat()}), 200
#         else:
#             return jsonify({"message": "No timestamps found"}), 404
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# Health check route
@app.route('/healthz')
def healthz():
    return "OK", 200


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)
