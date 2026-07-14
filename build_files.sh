#!/bin/bash
set -e

pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
