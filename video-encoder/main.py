import os
import clip
import torch
import logging
from PIL import Image
from pandas import DataFrame
from datetime import datetime
from uuid import uuid4 as uuid
from numpy import array, ndarray
from google.cloud import storage

log = logging.getLogger(__name__)

# consts
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
CREDENTIALS = os.getenv("GCP_ACCESS_KEY_PATH", './creds/secret.json')
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

def encode_image(loaded_image: Image) -> ndarray:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    collapsed_image = preprocess(loaded_image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(collapsed_image)
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
    
    # assemble output dataframe and ship to BigQuery
    features = { f'f{index}': feature for index, feature in enumerate(encoded_image.tolist()[0], 1) }
    features['frame_uuid'] = str(uuid())
    features['resource_uuid'] = str(uuid())
    features['timestamp_start'] = datetime.now().isoformat()
    features['timestamp_stop'] = datetime.now().isoformat()

    # df constructor requires iterable input in each column
    for key in features:
        features[key] = [features[key]]

    df = DataFrame(index=features['frame_uuid'],data=features)
    df.to_gbq()
    

if __name__ == '__main__':
    image = Image.open('./video-encoder/clip.png')

    # encode using model
    encoded_image = encode_image(image)

    # setup export via df
    features = { f'f{index}': feature for index, feature in enumerate(encoded_image.tolist()[0], 1) }
    features['frame_uuid'] = str(uuid())
    
    # emulate future of specying where in video seq frame is picked up
    features['resource_uuid'] = str(uuid())
    features['timestamp_start'] = datetime.now().isoformat()
    features['timestamp_stop'] = datetime.now().isoformat()

    # df constructor requires iterable for column values (just for now when doing images not video)
    for key in features:
        features[key] = [features[key]]

    df = DataFrame(index=features['frame_uuid'],data=features)
    df.to_gbq()