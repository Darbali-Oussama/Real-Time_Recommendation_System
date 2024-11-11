#from kafka import KafkaProducer
import json
#from ..models import UserRatingRequest

#producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def send_request_to_kafka(request: dict):
    pass
    # Publish the user rating data to Kafka

    # producer.send("recommendation_requests", value=request.dict())
    # producer.flush()
