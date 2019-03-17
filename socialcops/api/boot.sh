#!/bin/sh
source venv/bin/activate

echo Executing Database Upgrade Operation
flask db upgrade
echo Done!!

echo Generating Fake Dataset
python data.py
echo Done!!

echo Starting Gunicorn
exec gunicorn -b :5000 --workers 3 --access-logfile - --error-logfile - main:app
