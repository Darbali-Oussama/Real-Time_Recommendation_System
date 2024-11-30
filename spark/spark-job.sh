#!/bin/bash
cd /opt/bitnami/spark &&
pip install -r requirements.txt &&
spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3,org.postgresql:postgresql:42.2.20 recommendation.py