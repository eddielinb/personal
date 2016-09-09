# Web UI

Django based UI for checking meter protocols

## Setup
```
git clone ...
```
### Development
Run the lightweight development server using: `$ python manage.py runserver`
#### Virtualenv
```
cd /path/to/protocol_checker
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
#### Docker
```
cd /path/to/protocol_checker/protocol_checker
docker build -t pc_dev .
docker run -it --rm -p 8000:8000 pc_dev
```

## Admin User
`$ . ./reload.sh` or `$ python manage.py loaddata checker/ConfigController_data.json`
+ Username: `IMT`
+ Password: `informetis`

## Directory Structure
```
protocol_checker
│   README.md
│   manage.py
│   db.sqllite3
│
├───emulator
│   │   README.md
│   │   manage.py
│
└───protocol_checker
    │   README.md
    │   manage.py
    │   db.sqllite3
    │
    ├───protocol_checker
    │   │   settings.py
    │   │   urls.py
    │
    └───checker
        │   url.py
        │
        ├───views
        │   │   views_client.py
        │   │   views_meter.py
        │   │   views_shared.py
        │
        ├───templates
        │   └───checker
        │       │   index.html
        │
        └───static
            └───checker
                │   

```

#### manage.py
+ Used to manage the django project.
+ `$ python manage.py runserver` starts the python development web server.

### protocol_checker
This directory manages the overall project.
`settings.py` - Project settings
`urls.py` - Routing of urls

## Dependencies
+ Django 1.9.8
+ django-widget-tweaks 1.4.1

## [Deployment](https://docs.djangoproject.com/en/1.9/howto/deployment/)
