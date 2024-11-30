from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import col, lit, udf, from_json
from pyspark.sql.types import StructType, StructField, StringType, FloatType, MapType, IntegerType, ArrayType
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
from functools import partial, reduce
import json

# Initialize Spark session
spark = SparkSession.builder \
    .appName("RecommendationEngine") \
    .config("spark.jars.packages", "org.postgresql:postgresql:42.2.20,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
    .getOrCreate()

# Kafka configuration
kafka_bootstrap_servers = "kafka1:19092,kafka2:19093,kafka3:19094"
input_topic = "recommendation_requests"
output_topic = "recommendation_responses"

# Schema for Kafka messages
kafka_message_schema = StructType([
    StructField("user_id", IntegerType(), True),
    StructField("ratings", MapType(StringType(), FloatType()), True)
])

# Load item embeddings from PostgreSQL
jdbc_url = "jdbc:postgresql://postgres_db:5432/mydb"
db_properties = {"user": "admin", "password": "changeme111", "driver": "org.postgresql.Driver"}

item_embeddings = spark.read.jdbc(url=jdbc_url, table="item_embeddings", properties=db_properties)

# Parse embedding from string to array
def parse_embedding(embedding_str):
    return json.loads(embedding_str)
parse_embedding_udf = udf(parse_embedding, ArrayType(FloatType()))
item_embeddings = item_embeddings.withColumn("embedding", parse_embedding_udf(col("embedding")))


# Define recommendation logic
def recommend_books(user_id, user_ratings, item_embeddings):
    user_ratings = {int(key): value for key, value in user_ratings.items()}
    rated_ids = list(user_ratings.keys())
    
    # Filter rated items
    rated_items = item_embeddings.filter(item_embeddings["id"].isin(rated_ids))
    get_user_rating_with_ratings = partial(lambda id, user_ratings: user_ratings.get(id, 0.0), user_ratings=user_ratings)
    get_user_rating_udf = udf(lambda id: get_user_rating_with_ratings(id), FloatType())
    rated_items = rated_items.withColumn("label", get_user_rating_udf(col("id")))
    
    # Prepare features
    embedding_columns = [col("embedding")[i].alias(f"embedding_{i}") for i in range(100)]  # Assuming 100 dimensions
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
    item_embeddings = item_embeddings.withColumn("similarity", similarity_expr)
    
    # Get top recommendations
    recommendations = (
        item_embeddings
        .filter(~col("id").isin(rated_ids))
        .orderBy(col("similarity").desc())
        .limit(5)
        .select("title")
    )
    return [row["title"] for row in recommendations.collect()]

# Read Kafka stream
kafka_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", input_topic) \
    .option("startingOffsets", "latest") \
    .load()

# Deserialize Kafka value to JSON
kafka_stream = kafka_stream.selectExpr("CAST(value AS STRING) as message")
parsed_stream = kafka_stream.withColumn("message", from_json(col("message"), kafka_message_schema)).select("message.*")

# Process stream and generate recommendations
def process_batch(batch_df, batch_id):
    # Process each row in the batch
    for row in batch_df.collect():
        user_id = row["user_id"]
        user_ratings = row["ratings"]
        recommendations = recommend_books(user_id, user_ratings, item_embeddings)
        
        # Prepare response as a JSON string
        response = json.dumps({
            "user_id": user_id,
            "recommendations": recommendations
        })
        
        # Create a DataFrame with the required schema for Kafka
        response_df = spark.createDataFrame(
            [Row(value=response)]
        )
        
        # Write to Kafka
        response_df.write \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
            .option("topic", output_topic) \
            .save()


# Write output back to Kafka
parsed_stream.writeStream \
    .foreachBatch(process_batch) \
    .start() \
    .awaitTermination()
