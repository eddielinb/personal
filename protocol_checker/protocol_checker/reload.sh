#!/bin/bash

# run like $ . ./reload.sh
echo UnMigrating
python manage.py migrate --noinput checker zero
echo Migrating
python manage.py migrate --noinput checker
echo Loading
python manage.py loaddata checker/ConfigController_data.json
echo Running
python manage.py runserver
