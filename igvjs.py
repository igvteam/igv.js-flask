import requests
import re
import os
import pysam
import urllib
from flask import Flask, Response, request, abort, jsonify

app = Flask(__name__)

# default config values
app.config.update(dict(
    ALLOWED_EMAILS = 'allowed_emails.txt',
    USES_OAUTH = True,
    PUBLIC_DIR = None
))
# override with values from _config.py
app.config.from_object('_config')

seen_tokens = set()

# routes
@app.route('/')
def show_vcf():
    return app.send_static_file('str-dev.html')

@app.route('/data/<path:path>')
def get_data_list(path):
    #print request.headers
    basedir = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(basedir, path)
    json_results = {'dirs': [], 'files': []}
    executables = ['.vcf', '.vcf.gz', '.bam']
    for filename in os.listdir(path):
        full_path = os.path.join(abs_path, filename)
        if not os.path.isfile(full_path):
            data = {
                'name': filename,
                'path': path+'/'+filename
            }
            json_results['dirs'].append(data)
        else:
            if allowed_ending(filename, executables):
                data = {
                    'name': filename,
                    'displayName': filename[:filename.find('.')].replace('_', ' '),
                    'path': path+'/'+filename,
                }
                json_results['files'].append(data)
    # sort
    try:
        def compare(file):
            first = file['name'].rfind('_')
            second = file['name'].find('.')
            return int(file['name'][first+1:second])
        json_results['files'].sort(key=compare)
    except ValueError:
        json_results['files'].sort()
    rv = jsonify(json_results)
    #rv.headers['Access-Control-Allow-Origin'] = '*'
    return rv

@app.route('/alignments')
def alignments():
    reference = "alignments/" + request.args.get('reference') + ".fa"
    filename = "alignments/" + request.args.get('file')
    region = request.args.get('region')
    options = request.args.get("options")
    try:
        if options:
            return pysam.view(urllib.unquote(options), "-T", reference, filename, region)
        else:
            return pysam.view("-T", reference, filename, region)
    except pysam.SamtoolsError as e:
        return e.value

@app.before_request
def before_request():
    if app.config['USES_OAUTH'] and (not app.config['PUBLIC_DIR'] or \
            not os.path.exists('.'+app.config['PUBLIC_DIR']) or \
            not request.path.startswith(app.config['PUBLIC_DIR'])):
        auth = request.headers.get("Authorization", None)
        if auth:
            token = auth.split()[1]
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
            if "static/data" in request.path and "data/static/data" not in request.path:
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

def allowed_ending(string, endings):
    for ending in endings:
        if string.endswith(ending):
            return True
    return False
