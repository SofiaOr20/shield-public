#!/bin/sh
echo "Starting migrations for project..."
python /code/manage.py makemigrations
python /code/manage.py migrate --noinput
echo "Starting migrations for app..."
python /code/manage.py makemigrations api
python /code/manage.py migrate api --noinput
echo "Migrations ended!"
python /code/manage.py createcustomsuperuser
python /code/manage.py collectstatic --noinput
exec "$@"