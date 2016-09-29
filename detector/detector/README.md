# Detector UI

Django based Web UI for viewing data from local resources including:
+ Power consumption data
+ Waveforms and differences

Run the lightweight development server using: `$ python manage.py runserver`

## Directory Structure
```
detector_new
│   README.md
│   manage.py
│   db.sqllite3
│
├───detector_new
│   │   settings.py
│   │   urls.py
│   │   wsgi.py
│
│───detector
│   │   views.py
│   │   urls.py
│   │───templates
│   │   └───detector
│   │       ├───detector.html
│   │       └───footer.html
│   │
│   └───static
│         └───detector
│             ├───detector_graph.js
│             ├───shared_form_utils.js
│             ├───shared_graph_settings.js
│             ├───shared_graph_utils.js
│             ├───shared_utils.js
│             └───style.css

```

#### manage.py
+ Used to manage the django project.
+ `$ python manage.py runserver` starts the python development web server.


#### detector
This directory manages the overall project.
+ `settings.py` - Project settings
+ `urls.py` - Routing of urls

#### detector_view
+ This directory contains the detector application

#### templates
+ `index.html` - Html file containing the homepage
+ `footbar.html` - Html file containing the site wide footer

#### static
+ `shared_utils.js` - IMT.zip, IMT.logger, IMT.colour - Utility functions
+ `shared_form_utils.js` - IMT.form, IMT.time
+ `shared_graph_utils.js` - IMT.graph - JS graph utility functions
+ `shared_graph_settings.js` - IMT.graph.options -  Highcharts options
+ `shared_style.css` - Main css file

#### views.py
`views.py` - Functions for retrieving and serving data to the client
  + index() - renders detector.html and passes:
  + post_data() - serves json data based on a post request
  + scale_estimated() - scale the estimation value
  + get_waveforms() - retrieve waveforms and diff data
  + get_data() - retrieve local files depending on the post request