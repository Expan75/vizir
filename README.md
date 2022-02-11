# README

Vizir aims to demonstrate a multi-modal search model applied to video and its potential usecases.
This project is split into two components, both of which are deployed as seperate FAAS on GCP, they rely on cloud storage and BigQuery.

```console
# encodes storage uploaded videos and enables similarity calculations across features
/upload-encoder

# exposes a small webservice that allows semantic search on videos
/query-encoder 
```

# Deployment

Note that this section will change heavily after introducing Terraform and GitHub actions.

### Deploy file upload triggerd video encoder

```console

cd ./video-encoder
gcloud functions deploy video-encoder-dev --runtime python37 --trigger-resource vizir-media-uploads --trigger-event google.storage.object.finalize --entry-point on_upload --memory 2048
```

### Deploy HTTP triggered query encoder

```console
gcloud functions deploy FUNCTION_NAME
 --runtime python37 --trigger-http --allow-unauthenticated
```