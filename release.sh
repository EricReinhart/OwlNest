#!/bin/bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput
echo "from nest.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell 
gunicorn OwlNest.wsgi:application -c /code/gunicorn.conf