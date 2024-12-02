import os

from google.cloud import bigquery
from google.oauth2 import service_account


BIGQUERY_PROJECT = os.environ.get("BIGQUERY_PROJECT")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.environ.get("BIGQUERY_TABLE")
CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH")


def insert_data_into_bigquery(rows):
    if not rows:
        print("No new data to insert into BigQuery.")
        return

    # BigQuery client
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
    client = bigquery.Client(credentials=credentials)

    # BigQuery table
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"

    rows_to_insert = [
        {
            "id": row[0],
            "user_id": row[1],
            "book": row[2],
            "rating": row[3],
            "timeQuestion": row[4].isoformat(),
        }
        for row in rows
    ]

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"Encountered errors while inserting rows: {errors}")
    else:
        print(f"Successfully inserted {len(rows_to_insert)} rows into BigQuery.")



# # Batch Inserts freetier
# import csv

# def insert_data_into_bigquery(rows):

#     credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)

#     client = bigquery.Client(credentials=credentials)
#     table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
    
#     # Save rows to a temporary CSV file
#     temp_file = "temp_user_rating.csv"
#     with open(temp_file, "w", newline="") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(["id", "user_id", "book", "rating", "timeQuestion"])
#         writer.writerows(rows)
    
#     # Load CSV into BigQuery
#     job_config = bigquery.LoadJobConfig(
#         source_format=bigquery.SourceFormat.CSV,
#         skip_leading_rows=1,
#         autodetect=True,
#     )
    
#     with open(temp_file, "rb") as source_file:
#         job = client.load_table_from_file(source_file, table_id, job_config=job_config)
    
#     job.result()  # Wait for the job to complete
#     print(f"Inserted {len(rows)} rows into {table_id}.")
