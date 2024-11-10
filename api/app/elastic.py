from config import settings
from elasticsearch import Elasticsearch
# Initialize ES with configuration settings
es = Elasticsearch(
    settings.ES_HOST,
    basic_auth=(settings.ES_USER, settings.ES_PASS),
    ca_certs=settings.ca_cert
    # verify_certs=False
)