from sqlalchemy.orm import Session
from models import ItemEmbedding
from cache import redis_client
import json
import numpy as np

def get_item_embedding_by_title(db: Session, title: str):
    return db.query(ItemEmbedding.embedding).filter(ItemEmbedding.title == title).first()

def get_item_embedding_by_title(db: Session, title: str):
    cache_key = f"embedding:{title}"
    cached_embedding = redis_client.get(cache_key)
    
    # if cached_embedding:
    #     embedding = pickle.loads(cached_embedding)
    # else:
    #     result = db.query(ItemEmbedding.embedding).filter(ItemEmbedding.title == title).first()
    #     if result is None:
    #         return None
    #     #embedding = result[0]
    #     embedding = np.array(result).flatten().tolist()
    #     redis_client.set(cache_key, pickle.dumps(embedding))

    # return embedding

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

# def get_similar_titles(db: Session, embedding, limit=5):
#     return (
#         db.query(ItemEmbedding.title)
#         .order_by(ItemEmbedding.embedding.l2_distance(embedding))
#         .limit(limit)
#         .all()
#     )

def get_similar_titles(db: Session, embedding, limit=5):
    # Query the database to find similar titles based on the embedding
    results = (
        db.query(ItemEmbedding.title, ItemEmbedding.embedding)
        .order_by(ItemEmbedding.embedding.l2_distance(embedding))
        .limit(limit)
        .all()
    )

    # Process each result and only cache if it doesn't already exist in Redis
    similar_items = []
    for title, item_embedding in results:
        # Prepare the cache key
        cache_key = f"embedding:{title}"

        # Check if the item is already cached
        if not redis_client.exists(cache_key):
            # Format the data as a JSON object to store in Redis
            data = np.array(item_embedding).flatten().tolist()
            # Store in Redis
            redis_client.set(cache_key, json.dumps(data))

        # Append the title to the list of similar items to return
        similar_items.append(title)

    return similar_items


