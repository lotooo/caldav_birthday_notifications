#!/bin/bash
echo "Preparing virtualenv"
if [[ ! -d venv ]];then
    virtualenv -p python3 venv
fi
source venv/bin/activate

echo "Installing dependancies"
pip install -q -r requirements.txt

test -f .env && . .env

echo "Starting $0"
python exporter.py
