#!/bin/sh

# Activate the Python virtual environment, if any
# source /path/to/your/venv/bin/activate

# Change directory to the root project directory. Adjust the path if necessary.
cd /home/site/wwwroot/

# Start Gunicorn. Replace `app:app` with the import path to your WSGI application.
gunicorn --bind=0.0.0.0:8000 app:app
