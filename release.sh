#!/bin/bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn OwlNest.wsgi:application -c /code/gunicorn.conf