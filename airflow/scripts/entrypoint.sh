#!/bin/bash

set -e
#if [ -e "/usr/local/airflow/requirements.txt" ]; then
if [ -e "/opt/airflow/requirements.txt" ]; then
  $(command python) pip install --upgrade pip
  $(command -v pip) install -r requirements.txt
fi
if [ "$1" == "webserver" ]; then
if [ ! -f "/opt/airflow/airflow.db" ]; then
  airflow db init && \
  airflow users create \
    --username admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email admin@example.com \
    --password admin
fi
fi


$(command -v airflow) db upgrade

exec airflow $1