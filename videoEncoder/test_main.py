import os
import main
import pytest
from PIL import Image

if 'video-encoder' in os.getcwd():
    TEST_IMAGE_PATH = os.path.join(os.getcwd(), 'clip.png')
else:
   TEST_IMAGE_PATH = os.path.join(os.getcwd(), 'video-encoder/clip.png')

def test_embeddings_generator():
    image = Image.open(TEST_IMAGE_PATH)
    embeddings = main.generate_image_embeddings(image)
    assert(embeddings != None)
    assert(len(embeddings) == 512)

def test_prepare_export():
    required_keys = ['embeddings', 'frame_uuid', 'video_uuid', 'frame_timestamp']
    mock_embeddings = [n for n in range(0,512)]
    rows = main.prepare_feature_export(mock_embeddings)
    assert(len(rows) == 1)
    assert(list(rows[0].keys()) == required_keys)
    assert(len(rows[0]['embeddings']) == 512)

def test_on_upload():
    assert(True)