from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

def create_topics():
    # Kafka configuration
    bootstrap_servers = ['kafka1:19092', 'kafka2:19093', 'kafka3:19094']
    topics_to_create = [
        {"name": "recommendation_requests", "num_partitions": 3, "replication_factor": 1},
        {"name": "recommendation_responses", "num_partitions": 3, "replication_factor": 1},
    ]

    # Initialize KafkaAdminClient
    admin_client = KafkaAdminClient(
        bootstrap_servers=bootstrap_servers,
        client_id="topic_creator"
    )

    # Create topics
    for topic in topics_to_create:
        try:
            new_topic = NewTopic(
                name=topic["name"],
                num_partitions=topic["num_partitions"],
                replication_factor=topic["replication_factor"]
            )
            admin_client.create_topics([new_topic])
            print(f"Topic '{topic['name']}' created successfully!")
        except TopicAlreadyExistsError:
            print(f"Topic '{topic['name']}' already exists.")
        except Exception as e:
            print(f"Failed to create topic '{topic['name']}': {e}")

    # Close the admin client
    admin_client.close()

# Only execute the topic creation if the script is run directly
if __name__ == "__main__":
    create_topics()
