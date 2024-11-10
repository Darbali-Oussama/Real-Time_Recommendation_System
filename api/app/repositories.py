from sqlalchemy.orm import Session
from models import ItemEmbedding
from config import settings
from cache import redis_client
from elastic import es
import json
import numpy as np

def get_item_embedding_by_title_postgres(db: Session, title: str):
    cache_key = f"embedding:{title}"
    cached_embedding = redis_client.get(cache_key)
    if cached_embedding:
        # Decode the JSON string back into a Python list
        embedding = json.loads(cached_embedding)
    else:
        # Query the database for the embedding
        result = db.query(ItemEmbedding.embedding).filter(ItemEmbedding.title == title).first()
        if result is None:
            return None
        # Convert the embedding to a list
        embedding = np.array(result).flatten().tolist()
        # Store the embedding in Redis as a JSON-encoded string
        redis_client.set(cache_key, json.dumps(embedding))

    return embedding

def get_similar_titles_postgres(db: Session, embedding, limit=5):
    # Query the database to find similar titles based on the embedding
    results = (
        db.query(ItemEmbedding.title, ItemEmbedding.embedding)
        .order_by(ItemEmbedding.embedding.l2_distance(embedding))
        .limit(limit)
        .all()
    )

    # Process each result and only cache if it doesn't already exist in Redis
    similar_items = []
    for title, embedding in results:
        # Prepare the cache key
        cache_embedding_in_redis(title, embedding)
        similar_items.append(title)

    return similar_items

def get_embedding_from_elasticsearch(title: str):
    cache_key = f"embedding:{title}"
    cached_embedding = redis_client.get(cache_key)
    if cached_embedding:
        # Decode the JSON string back into a Python list
        embedding = json.loads(cached_embedding)
    else:
        search_query = {
            "query": {
                "match": {
                    "title": title
                }
            }
        }
        response = es.search(index=settings.ES_index_name, body=search_query)
        if response['hits']['hits']:
            embedding = response['hits']['hits'][0]['_source']['embedding']
            embedding = np.array(embedding).flatten().tolist()
            redis_client.set(cache_key, json.dumps(embedding))

    return embedding

def get_similar_titles_elasticsearch(embedding, limit=5):
    # Query the database to find similar titles based on the embedding
    similarity_query = {
        "size": limit,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {
                        "query_vector": embedding
                    }
                }
            }
        }
    }

    response = es.search(index=settings.ES_index_name, body=similarity_query)
    results = []
    for hit in response['hits']['hits']:
        title = hit['_source']['title']
        embedding = hit['_source']['embedding']
        
        # Cache embedding if it is not in Redis
        cache_embedding_in_redis(title, embedding)

        results.append(title)

    return results


def cache_embedding_in_redis(title: str, embedding):
    cache_key = f"embedding:{title}"
    if not redis_client.exists(cache_key):
        embedding = np.array(embedding).flatten().tolist()
        redis_client.set(cache_key, json.dumps(embedding))