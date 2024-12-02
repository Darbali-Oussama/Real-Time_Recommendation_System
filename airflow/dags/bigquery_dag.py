from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from utils.postgres_utils import fetch_data_from_postgres
from utils.bigquery_utils import insert_data_into_bigquery


start_date = datetime(2024, 10, 28, 10)

default_args = {
    "owner": "airflow",
    "start_date": start_date,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def fetch_data():
    return fetch_data_from_postgres()

def insert_data(**kwargs):
    rows = kwargs['ti'].xcom_pull(task_ids='fetch_postgres_data')
    if rows is None:
        raise ValueError("No data found from fetch_postgres_data")
    insert_data_into_bigquery(rows)

with DAG(
    dag_id="postgres_to_bigquery_hourly",
    default_args=default_args,
    description="Transfer new user ratings from PostgreSQL to BigQuery every hour",
    schedule_interval="0 * * * *",  # Every hour
    catchup=False,
) as dag:

    fetch_postgres_data = PythonOperator(
        task_id="fetch_postgres_data",
        python_callable=fetch_data,
    )

    insert_bigquery_data = PythonOperator(
        task_id="insert_bigquery_data",
        python_callable=insert_data,
        provide_context=True,
    )

    fetch_postgres_data >> insert_bigquery_data