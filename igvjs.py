import requests
import re
import os
from flask import Flask, Response, request, abort

app = Flask(__name__)

# default config values
app.config.update(dict(
    ALLOWED_EMAILS = 'allowed_emails.txt',
    USES_OAUTH = False,
    PUBLIC_DIR = '/static/data/public'
))
# override with values from _config.py
app.config.from_object('_config')

seen_tokens = set()

# routes
@app.route('/')
def show_igv():
    return app.send_static_file('igv.html')

@app.before_request
def before_request():
    #print request.headers
    if app.config['USES_OAUTH'] and (not app.config['PUBLIC_DIR'] or \
            not os.path.exists('.'+app.config['PUBLIC_DIR']) or \
            not request.path.startswith(app.config['PUBLIC_DIR'])):
        auth = request.headers.get("Authorization", None)
        if auth:
            token = auth.split()[1]
            #print request.path
            if token not in seen_tokens:
                google_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
                params = {'access_token':token}
                res = requests.get(google_url, params=params)
                email = res.json()['email']
                if email in allowed_emails():
                    seen_tokens.add(token)
                else:
                    abort(403)
        else:
            if "static/data" in request.path:
                abort(401)
    return ranged_data_response(request.headers.get('Range', None), request.path[1:])

def allowed_emails():
    emails = []
    if os.path.isfile(app.config['ALLOWED_EMAILS']):
        with open(app.config['ALLOWED_EMAILS'], 'r') as f:
            for line in f:
                emails.append(line.strip())
    return emails

def ranged_data_response(range_header, path):
    if not range_header:
        return None
    m = re.search('(\d+)-(\d*)', range_header)
    if not m:
        return "Error: unexpected range header syntax: {}".format(range_header)
    size = os.path.getsize(path)
    offset = int(m.group(1))
    length = int(m.group(2) or size) - offset

    data = None
    with open(path, 'rb') as f:
        f.seek(offset)
        data = f.read(length)
    rv = Response(data, 206, mimetype="application/octet-stream", direct_passthrough=True)
    rv.headers['Content-Range'] = 'bytes {0}-{1}/{2}'.format(offset, offset + length-1, size)
    return rv
