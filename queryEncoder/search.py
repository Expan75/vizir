import os
import torch
import clip
from google.cloud import bigquery
from pprint import pprint as pp

# Settings
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_CREDENTIALS = os.getenv("GCP_CREDENTIALS", "./creds/secret.json")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "vizir_development")
BQ_TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.video_embeddings"

# TODO: the query should include frame metadata and be neatly organised
RECS_QUERY = f""" 
  WITH et as (SELECT Array(SELECT embeddings.value
  FROM {BQ_TABLE_ID} as ve
  CROSS JOIN UNNEST(ve.embeddings) as embeddings))

  SELECT * FROM et;
"""

# Ensure model load only runs on cold start, see https://cloud.google.com/functions/docs/concepts/exec
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)


def generate_query_embeddings(query: str) -> list:
  """Encodes a query strings into embeddings"""
  with torch.no_grad():
    text_inputs = torch.cat([clip.tokenize(f"{query}")]).to(device)
    text_features = model.encode_text(text_inputs).tolist()[0]
  return text_features


def translate(raw_query: str) -> str:
  """Placeholder if we want to be fancy"""
  pass


def by_string(query: str) -> list:
  """Initaties the video search flow by generating text embeddings
     and then compares them to the video embeddings on BQ (via cos simularity, see query)
  """
  # translate query into comparable embeddings
  text_embeddings = generate_query_embeddings(query)

  # compare /w video embeddings from BQ and return the most relevant
  bq = bigquery.Client.from_service_account_json(GCP_CREDENTIALS)
  q = RECS_QUERY

  results = bq.query(q).result()
  
  # return slightly restructured results
  return list(results)

if __name__ == "__main__":
  recs = by_string('hello there')
  print("results: ")
  pp(recs)