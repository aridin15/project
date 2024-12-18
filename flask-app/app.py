import os
import json
import threading
import time
from google.cloud import secretmanager
from flask import Flask
from pymongo import MongoClient
import logging
import requests


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('flask')

def get_public_ip():
    try:
        response = requests.get('http://ipinfo.io/ip')
        print("response ip is: ", response)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

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

def periodic_mongo_write():
    while True:
        try:
            # Create a new MongoDB client for the thread
            print("did it connect?")
            thread_client = setup_mongodb_connection()
            thread_db = thread_client["mashcantas-dev-db-cluster"]
            thread_collection = thread_db["dev_tests_v01"]
            print("yes")
            # Insert document
            test_document = {"message": "Periodic write from Flask app!"}
            thread_collection.insert_one(test_document)
            logger.info("Document inserted into MongoDB by background thread.")
        except Exception as e:
            logger.error(f"Error in background MongoDB thread: {e}")
        finally:
            time.sleep(30)  # Write every 30 seconds

def start_background_thread():
    if not hasattr(app, "background_thread"):
        app.background_thread = threading.Thread(target=periodic_mongo_write, daemon=True)
        app.background_thread.start()

# Health check route
@app.route('/healthz')
def healthz():
    try:
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
    start_background_thread()
    app.run(host='0.0.0.0', port=5000)
