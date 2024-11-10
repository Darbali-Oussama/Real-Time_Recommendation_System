#!/bin/bash
apt-get update
pip install --upgrade pip
cd app
pip install -r requirements.txt
python3 -m uvicorn --host 0.0.0.0 --port 8000 --reload main:app