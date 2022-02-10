import os
import clip
import torch
import logging
from PIL import Image
from datetime import datetime
from uuid import uuid4 as uuid
from google.cloud import storage, bigquery

log = logging.getLogger(__name__)

# Settings
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
GCP_CREDENTIALS = os.getenv("GCP_CREDENTIALS", './creds/secret.json')
BQ_DATASET_ID = os.getenv('BQ_DATASET_ID', "vizir_development")
BQ_TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.video_embeddings"
BQ_TABLE_SCHEMA = [
    bigquery.SchemaField('video_uuid', 'STRING'),
    bigquery.SchemaField('frame_uuid', 'STRING'),
    bigquery.SchemaField('frame_timestamp', 'STRING'),
    bigquery.SchemaField('embeddings', 'RECORD', mode='REPEATED', fields=[
        bigquery.SchemaField('value', 'FLOAT64')
    ]),
]

def get_uploaded_image(bucketname: str, filename: str) -> Image:
    """Downloads and parses the specified imagefile in a given bucket"""
    client = storage.Client()
    bucket = client.bucket(bucketname)
    blob = bucket.blob(filename)

    if blob.exists():
        with blob.download_as_bytes as bytes:
            return Image.open(bytes)
    else:
        log.error("no file found of name %s in bucket %s, exiting..." % (filename, bucketname))
        exit()

def encode_image(loaded_image: Image):
    """Encodes an image """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    collapsed_image = preprocess(loaded_image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(collapsed_image).tolist()[0]
    return image_features

def on_upload(event: dict, context):
    """Responds to movie clip uploads to GCP buckets and encodes the contents.
       The encoded content is exported to BigQuery were it enables semantic search on frames.
    """
    bucketname = event.get('bucket')
    filename = event.get('name')
    image = get_uploaded_image(bucketname, filename)

    # encode using model
    encoded_image = encode_image(image)
    
    # setup export data structure
    features = {}
    features['frame_embeddings'] = encoded_image
    features['frame_uuid'] = str(uuid())
    features['video_uuid'] = str(uuid())
    features['video_section_start'] = datetime.now().isoformat()
    features['video_section_stop'] = datetime.now().isoformat()
    
    pass

if __name__ == '__main__':
    image = Image.open('./clip.png')

    # encode using model
    encoded_image = encode_image(image)

    # setup export data structure
    features = {}
    features['embeddings'] = [{ "value": value } for value in encoded_image]
    features['frame_uuid'] = str(uuid())
    features['video_uuid'] = str(uuid())
    features['frame_timestamp'] = datetime.now().isoformat()

    rows = [
        features
    ]

    bq = bigquery.Client.from_service_account_json(GCP_CREDENTIALS)
    errors = bq.insert_rows_json(BQ_TABLE_ID, rows)
    if errors:
        print(errors)
        raise Exception('Errors occured when writing to BQ')