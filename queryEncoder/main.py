import os
import logging
import search
import functions_framework
from google.cloud import bigquery
from flask import render_template, abort

log = logging.getLogger(__name__)

# Settings
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_CREDENTIALS = os.getenv("GCP_CREDENTIALS", "./creds/secret.json")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "vizir_development")
BQ_TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.video_embeddings"

@functions_framework.http
def index(request):
    if request.method == "POST":
        query = request.form.get("query") # no validation; spooky stuff
        recommendations = search.by_string(query)
        return render_template(
            "results.html", 
            title="Result | Vizir",
            recommendations=recommendations,
            query=query
        )
    elif request.method == "GET":
        return render_template("landing.html", title="Search | Vizir")
    else:
        abort(404)