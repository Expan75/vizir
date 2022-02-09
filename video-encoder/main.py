import os
import logging
from PIL import Image
from pandas import DataFrame
from numpy import array, ndarray
from google.cloud import storage

log = logging.getLogger(__name__)

# consts
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
CREDENTIALS = './creds/secret.json'
BQ_TABLE__NAME = os.getenv('GCP_BQ_TABLE_NAME')
BQ_TABLE_SCHEMA = [{
    'name': 'col1', 'type': 'STRING'
}]

def get_uploaded_image(bucketname: str, filename: str) -> Image:
    client = storage.Client()
    bucket = client.bucket(bucketname)
    blob = bucket.blob(filename)

    if blob.exists():
        with blob.download_as_bytes as bytes:
            return Image.open(bytes)
    else:
        log.error("no file found of name %s in bucket %s, exiting..." % (filename, bucketname))
        exit()

def encode_image(image: Image) -> ndarray:
    pass

def on_upload(event: dict, context):
    """Responds to movie clip uploads to GCP buckets and encodes the contents.
       The encoded content is exported to BigQuery were it enables semantic search on frames.
    """
    bucketname = event.get('bucket')
    filename = event.get('name')
    image = get_uploaded_image(bucketname, filename)

    # encode using model
    
    # construct output dataframe

    # ship to BigQuery