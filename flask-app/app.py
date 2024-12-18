import os
import json
import requests
from google.cloud import secretmanager
from flask import Flask
from pymongo import MongoClient
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('flask')

def access_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    print("ariel 2")
    """
    Access the secret from Google Cloud Secret Manager
    """
    client = secretmanager.SecretManagerServiceClient()
    print("client is: ", client)
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        # logger.error(f"Error accessing secret: {e}")
        raise

def setup_mongodb_connection():
    print("ariel 1")
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
        # client = MongoClient(mongo_uri, tls=True, tlsAllowInvalidCertificates=True)
        client = MongoClient(mongo_uri)

        # Test the connection
        # client.admin.command('ping')
        # logger.debug("Successfully connected to MongoDB!")

        return client
    except Exception as e:
        # logger.error(f"Failed to connect to MongoDB: {e}")
        raise

# Initialize MongoDB connection when app starts
try:
    print("ariel5")
    mongo_client = setup_mongodb_connection()

    db = mongo_client["mashcantas-dev-db-cluster"]  # Replace with your database name
    collection = db["dev_tests_v01"]  # Replace with your collection name
except Exception as e:
    # logger.error(f"Failed to initialize MongoDB: {e}")
    raise

# Health check route
@app.route('/healthz')
def healthz():
    try:
        mongo_client.admin.command('ping')
        return "OK", 200
    except Exception as e:
        # logger.error(f"MongoDB connection failed: {e}")
        return "MongoDB connection failed", 500

@app.route('/api/flask')
def hello_world():
    # Insert a test document into MongoDB
    test_document = {"message": "Hello from Flaskyy!"}
    collection.insert_one(test_document)

    return 'Hello, World from Flasky! Document inserted into MongoDB!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
