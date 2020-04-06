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

Alternatively, you can set the environment variable FLASK_APP to igvjs.py and use 'flask run':
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
