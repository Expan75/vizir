# README

Vizir aims to demonstrate a multi-modal search model applied to video and its potential usecases.
This project is split into two components, both of which are deployed as seperate FAAS on GCP, they rely on cloud storage and BigQuery.

```console

	# encodes storage uploaded videos and enables similarity calculations across features
	/upload-encoder

	# exposes a small webservice that allows semantic search on videos
	/query-encoder 

```
