from pyspark.sql import SparkSession
from pyspark.sql.functions import col, array, lit, sum, udf
from pyspark.sql.types import ArrayType, FloatType
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
from kafka import KafkaConsumer, KafkaProducer
from functools import partial
from functools import reduce
import json
import ast

# Initialize Spark session
spark = SparkSession.builder \
    .appName("RecommendationEngine") \
    .config("spark.jars.packages", "org.postgresql:postgresql:42.2.20,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
    .getOrCreate()

# Kafka setup
consumer = KafkaConsumer(
    'recommendation_requests',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Convert embedding from string to array
def parse_embedding(embedding_str):
    return ast.literal_eval(embedding_str)
parse_embedding_udf = udf(parse_embedding, ArrayType(FloatType()))

# Add user ratings as label
def get_user_rating(id, user_ratings):
    return user_ratings.get(id, 0.0) 
#get_user_rating_udf = udf(get_user_rating, FloatType())
    
# Load item embeddings from PostgreSQL
jdbc_url = "jdbc:postgresql://localhost:5432/mydb"
db_properties = {"user": "admin", "password": "changeme111", "driver": "org.postgresql.Driver"}

item_embeddings = spark.read.jdbc(url=jdbc_url, table="item_embeddings", properties=db_properties)
item_embeddings = item_embeddings.withColumn("embedding", parse_embedding_udf(col("embedding")))


# Function to handle user request and generate recommendations
def recommend_books(request_data):
    global item_embeddings
    
    user_id = request_data["user_id"]
    user_ratings = request_data["ratings"]

    # Filter out rated items and prepare features
    rated_titles = list(user_ratings.keys())
    rated_items = item_embeddings.filter(item_embeddings["id"].isin(rated_titles))

    # Bind the user_ratings dictionary to the function using partial
    get_user_rating_with_ratings = partial(get_user_rating, user_ratings=user_ratings)
    # Register the UDF with FloatType as the return type
    get_user_rating_udf = udf(lambda id: get_user_rating_with_ratings(id), FloatType())
    rated_items = rated_items.withColumn("label", get_user_rating_udf(col("id")))
    #rated_items = rated_items.withColumn("label", get_user_rating_udf(user_ratings, col("id")))

    # Vectorize the embeddings for model training
    embedding_columns = [col("embedding")[i].alias(f"embedding_{i}") for i in range(100)]  # Assuming 100 dimensions in your vector
    rated_items_flattened = rated_items.select(*embedding_columns, "label")
    assembler = VectorAssembler(inputCols=[f"embedding_{i}" for i in range(100)], outputCol="features")
    rated_items_transformed = assembler.transform(rated_items_flattened)

    # Train Ridge Regression model
    ridge_model = LinearRegression(featuresCol="features", labelCol="label", regParam=1.0, elasticNetParam=0.0)
    model = ridge_model.fit(rated_items_transformed)
    user_preferences = model.coefficients
    # Calculate similarity scores
    user_pref_array = [lit(val) for val in user_preferences.toArray()]
    similarity_expr = reduce(
        lambda acc, i: acc + (col("embedding")[i] * user_pref_array[i]), 
        range(len(user_preferences)), 
        lit(0.0)
    )
    my_embedd = item_embeddings.withColumn("similarity", similarity_expr)

    # Get top recommendations
    recommendations = (
        my_embedd
        .filter(~col("id").isin(rated_titles))
        .orderBy(col("similarity").desc())
        .limit(5)
        .select("title")
    )

    recommendations_list = [row["title"] for row in recommendations.collect()]
    
    # Send recommendations back to Kafka
    response = {"user_id": user_id, "recommendations": recommendations_list}
    producer.send("recommendation_responses", value=response)
    producer.flush()


# Listen for requests and process them
for message in consumer:
    recommend_books(message.value)