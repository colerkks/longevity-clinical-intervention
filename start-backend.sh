#!/bin/bash
# 启动后端服务器

echo "启动后端 API 服务器..."
cd "$(dirname "$0")/backend"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
