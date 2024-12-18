import os
import json
import threading
import time
from google.cloud import secretmanager
from flask import Flask
from pymongo import MongoClient
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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
        logger.error(f"Error accessing secret: {e}")
        raise

def setup_mongodb_connection():
    try:
        project_id = "mashcantas-dev"
        secret_id = os.environ.get("SECRET_ID", "mainMongoUri_dev")  # Default to your secret name
        mongo_secret = access_secret(project_id, secret_id)
        # Check if secret is a JSON or plain URI
        if mongo_secret.strip().startswith("{"):
            secret_dict = json.loads(mongo_secret)
            mongo_uri = secret_dict["MONGO_URI"]
        else:
            mongo_uri = mongo_secret.strip()

        # Create MongoDB client
        client = MongoClient(mongo_uri)

        # Test the connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")

        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

# Initialize MongoDB connection when app starts
try:
    mongo_client = setup_mongodb_connection()
    db = mongo_client["mashcantas-dev-db-cluster"]  # Replace with your database name
    collection = db["dev_tests_v01"]  # Replace with your collection name
except Exception as e:
    logger.error(f"Failed to initialize MongoDB: {e}")
    raise

# Background thread to write to MongoDB periodically
def periodic_mongo_write():
    while True:
        try:
            test_document = {"message": "Periodic write from Flask app!"}
            collection.insert_one(test_document)
            logger.info("Document inserted into MongoDB by background thread.")
        except Exception as e:
            logger.error(f"Error writing to MongoDB in background thread: {e}")
        time.sleep(30)  # Write every 30 seconds

# Start the background thread
thread = threading.Thread(target=periodic_mongo_write, daemon=True)
thread.start()

# Health check route
@app.route('/healthz')
def healthz():
    try:
        mongo_client.admin.command('ping')
        return "OK", 200
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return "MongoDB connection failed", 500

@app.route('/api/flask')
def hello_world():
    # Insert a test document into MongoDB
    test_document = {"message": "Hello from Flaskyy!"}
    collection.insert_one(test_document)

    return 'Hello, World from Flasky! Document inserted into MongoDB!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)