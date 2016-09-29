# Web UI

Django based Web UI for viewing data from various sources including:
+ imGate API
+ CSV files from google drive
+ Wave data from google drive

Run the lightweight development server using: `$ python manage.py runserver`

## Directory Structure
```
web_ui_project
│   README.md
│   manage.py
│   db.sqllite3
│   debug.log
│
├───web_ui_project
│   │   settings.py
│   │   urls.py
│   │   data-store-web-ui.json
│
├───home
│   │   urls.py
│   │   views.py    render index page
│   │   project_settings.py
│   │
│   ├───templates
│   │   ├───home
│   │   │   │   index.html
│   │   │
│   │   ├───web_ui
│   │   │   header.html
│   │   │   navbar.html
│   │   │   footer.html  loading all relevant javascripts and css files
│   │
│   └───static
│       └───web_ui
│           │   shared_utils.js             contains functions related to colours and logs
│           │   shared_graph_utils.js       contains functions to produce charts on graphs
│           │   shared_graph_settings.js    several graph settings as a base for use
│           │   shared_form_utils.js        contains functions related to forms
│           │   shared_style.css            simple shared style css for all pages
│
├───im
│   │   get_imGate.py
│   │   imgate_settings.py
│   │   internal_api_settings.py
│
├───im1
│   │   urls.py
│   │   views.py
│   │
│   ├───templates
│   │   └───im1
│   │       │   index.html
│   │
│   └───static
│       └───im1
│           │   im1_graph.js
│
├──im2
│   │   urls.py
│   │   views.py
│   │
│   ├───templates
│   │   └───im2
│   │       │   index.html
│   │
│   └───static
│       └───im2
│           │   im2_graph.js
│
├───csv1
│   │   urls.py
│   │   views.py
│   │
│   ├───templates
│   │   └───csv1
│   │       │   index.html
│   │
│   └───static
│       └───csv1
│           │   csv1_graph.js
│
└───gdrive1
    │   urls.py
    │   views.py
    │
    ├───templates
    │   └───gdrive1
    │       │   index.html
    │
    └───static
        └───gdrive1
            │   gdrive1_graph.js

```

#### manage.py
+ Used to manage the django project.
+ `$ python manage.py runserver` starts the python development web server.

#### debug.log
+ Logging log file
+ Must have R+W permissions

### web_ui
This directory manages the overall project.
+ `settings.py` - Project settings
+ `urls.py` - Routing of urls
+ `data-store-web-ui.json` - Google drive credentials, not included in the repo. Must have R+W permissions

### home
Homepage view, also storage for shared resources.
+ `urls.py` - Routing of urls to functions
+ `views.py` - Serves homepage
+ `project_settings.py` - Project wide python settings
#### templates
+ `index.html` - Html file containing the homepage
+ `header.html` - Html file containing the site wide header
+ `navbar.html` - Html file containing the site wide navbar
+ `footbar.html` - Html file containing the site wide footer
#### static
+ `shared_utils.js` - IMT.zip, IMT.logger, IMT.colour - Utility functions
+ `shared_form_utils.js` - IMT.form, IMT.time
+ `shared_graph_utils.js` - IMT.graph - JS graph utility functions   
+ `shared_graph_settings.js` - IMT.graph.options -  Highcharts options            
+ `shared_style.css` - Main css file      

### im1/im2/csv1/gdrive1
imGate API view
+ `urls.py` - Routing of urls to functions
+ `views.py` - Functions for retrieving and serving data to the client
  + index() - renders index.html and passes:
    + the values to populate the form with initially
    + mappings from numerical units to text meanings
  + post_data() - serves json data based on a post request
  + json_response() - serves json string to the client based on a post request
  + parse_request() - parses post request for the settings needed
  + get_json() - Gets the files from the relevant source
#### templates/\<name>
+ `index.html` - Html file containing the form and graphs, receives initial data from django, loads html and js files.
#### static/\<name>
+ `<name>graph.js` - Js file containing functions to process incoming json

### im
Shared python code for imGate API views

## Dependencies
+ modules / common
+ modules / gcp
+ Django 1.9.8
+ json
+ urllib2
+ Defaults:
    + imGate API server at `IP = "104.155.192.173"`, `PORT = "3000"`, `VERSION = "0.1"`
    + internal API server at `IP = "130.211.64.45"`, `PORT = "8080"`, `VERSION = "0.2"`

## Deployment

### Development
Set up your virtual environment:
```
cd /path/to/web_ui
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
There is a builtin lightweight python web server, start it using:
`$ python manage.py runserver`

### Docker
The docker configuration is based off of <https://github.com/GrahamDumpleton/mod_wsgi-docker>    
To build the docker file:
```
cd path/to/web_ui
docker build -t web_ui-app .
```
To run the docker container:
```
docker run -d -p 8000:80 --name web_ui-container web_ui-app
docker exec -it web_ui-container /bin/bash
python web_ui_project/manage.py collectstatic --noinput
exit
```
deprecated: `docker run -it --rm -p 8000:80 --name web_ui-container web_ui-app`


### [Production](https://docs.djangoproject.com/en/1.9/howto/deployment/)
This will use Apache, other methods are available
+ Install [Apache](https://httpd.apache.org/)
+ Install and activate [mod_wsgi](http://www.modwsgi.org/)
+ Add to config file, see `web_ui/apache_config/` for an example:
```
WSGIScriptAlias / /path/to/mysite.com/mysite/wsgi.py
WSGIPythonPath /path/to/mysite.com

<Directory /path/to/mysite.com/mysite>
<Files wsgi.py>
Require all granted
</Files>
</Directory>
```
+ [More insructions](https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/modwsgi/)
