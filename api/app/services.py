from sqlalchemy.orm import Session
from repositories import get_item_embedding_by_id_postgres, get_similar_items_postgres, get_embedding_from_elasticsearch, get_similar_titles_elasticsearch, send_request_to_kafka
from models import UserRating
from typing import List
from kafka import KafkaConsumer
import json

def get_recommendations_postgres(db: Session, item_id: int, limit: int = 5):
    # Get the embedding for the input title
    embedding = get_item_embedding_by_id_postgres(db, item_id)
    #embedding = np.array(embedding).flatten().tolist()
    if not embedding:
        return []
    
    # Find similar titles based on the embedding
    item_emnedding = get_similar_items_postgres(db, embedding, limit)
    return item_emnedding[1:]

def get_recommendations_elastic(title: str, limit: int = 5):
    # Get the embedding for the input title
    embedding = get_embedding_from_elasticsearch(title)
    if not embedding:
        return []
    
    # Find similar titles based on the embedding
    similar_titles = get_similar_titles_elasticsearch(embedding, limit)
    return [title for title in similar_titles[1:]]

def recommend_kafka_spark(db: Session, ratings: List[UserRating]):
    for rating in ratings:
        # Create UserRating instance with each rating in the list
        user_rating = UserRating(user_id=rating.user_id, book=rating.book, rating=rating.rating)
        db.add(user_rating)
    db.commit()

    # Prepare and send recommendation request to Kafka
    request_data = {
        "user_id": ratings[0].user_id,
        "ratings": {rating.book: rating.rating for rating in ratings}
    }
    send_request_to_kafka(request_data)
    
# Initialize Kafka consumer
consumer = KafkaConsumer(
        'recommendation_responses',  # Replace with your Kafka topic name
        bootstrap_servers=['kafka1:19092', 'kafka2:19093', 'kafka3:19094'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

def get_recommendations(user_id: int):
    for message in consumer:
        recommendation_data = message.value
        if recommendation_data.get("user_id") == user_id:
            recommendations = recommendation_data.get("recommendations", [])
            return recommendations