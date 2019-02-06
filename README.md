# IGV with Flask
An example project for integrating igv.js and [Flask](https://flask.pocoo.org/)

## Installation
You can install all required packages including Flask using [pip](https://pip.pypa.io/en/stable/).
```sh
pip install -r requirements.txt
```
## Running the app
To run the app using the simple builtin server, you can use the provided run file:
```sh
python run.py
```

Now that the server is running, go to (http://localhost:5000) to use IGV.
To view one of the example tracks, click on it in the box in the upper left corner.

Alternatively, you can set the environment variable FLASK_APP to ijvjs.py and use 'flask run':
```sh
export FLASK_APP=igvjs.py
flask run
```
Note: With this method, you can use the command-line options for flask run. For
example, use the -p option to set port number. Use --host=0.0.0.0 to make the
server externally visible (eg. flask run -p 8659 --host=0.0.0.0).

### Configuration
Configuration options can be set in _config.py in the root directory.

Currently supported options are:  
USES_OAUTH - whether or not data is protected using OAuth  
ALLOWED_EMAILS - the filename containing the list of allowed emails when using OAuth  
PUBLIC_DIR - path to directory of public data when using OAuth (eg. /static/data/public)

### Deployment
Flask is not meant to be a standalone/permanent hosting solution.
If you are intending to deploy this as an intranet service (Think carefully before exposing genomic data to an unprotected network) you may find it conveinent to route Flask through a proper web server such as Apache or Nginx. For this, Flask requires an intermediate layer which understands python such as Gunicorn or uWSGI. Gunicorn is native to python detects most settings automatically, but needs an accompanying daemon to keep it running in the background. uWSGI has native packages on most common distros, but requires a configuration such as the following.

for debian-based distros, the following are dependencies:
```
uwsgi-emperor uwsgi-plugin-python3 
```

This configuration assumes that this repository is cloned to 
/srv/igvjs/igvjs
and the virtualenv is created at
/srv/igvjs/virtualenvironment

```
virtualenv /srv/igvjs/virtualenvironment
source /srv/igvjs/virtualenv/bin/activate
pip3 install -r /srv/igvjs/igvjs/requirements.txt
```

/etc/uwsgi-emperor/vassals/igv.ini
```
[uwsgi]
plugins = python3
project = igvjs
uid = igv
gid = www-data
base = /srv/igvjs

chdir = %(base)/%(project)
home = %(base)/virtualenv
module = igvjs:app

master = true
processes = 5

socket = /run/uwsgi/%(project).sock
mount = /igv=%(module)
vacuum = true

; rewrite SCRIPT_NAME and PATH_INFO accordingly
manage-script-name = true
```

In this setup, an appropriate nginx directive would be 

```
    location /igv {
        uwsgi_pass unix:///run/uwsgi/igvjs.sock;
        include uwsgi_params;
    }
    location ^~ /static/ {
        alias /srv/igvjs/igvjs/igvjs/static;
    }
```
