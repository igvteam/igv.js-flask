import requests
import re
import os
import sys
from flask import Flask, Response, request, abort, jsonify, render_template, url_for
from flask_compress import Compress

app = Flask(__name__)

# default config values
app.config.update(dict(
    ALLOWED_EMAILS = 'allowed_emails.txt',
    USES_OAUTH = True,
    PUBLIC_DIR = None
))
# override with values from _config.py
app.config.from_object('_config')

Compress(app)

if app.config['ENABLE_CORS_REQUESTS']:
    from flask_cors import CORS, cross_origin
    CORS(app)

if app.config['ENABLE_ALIGNMENT_SERVICE']:
    try:
        import pysam
        from urllib import unquote
    except ImportError:
        print 'Alignments service is enabled but pysam is not installed. Please\
install pysam (pip install pysam) if you wish to use the alignments service.'

if app.config['ENABLE_UCSC_SERVICE']:
    try:
        import mysql.connector
    except ImportError:
        print 'UCSC service is enabled but mysql.connector is not installed. Please\
install mysql-connector (pip install mysql-connector==2.1.4) if you wish to use the UCSC service.'

seen_tokens = set()

# routes
@app.route('/')
def show_vcf():
    return render_template('igv.html')

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
    if 'pysam' not in sys.modules:
        return 'Either you have not enabled the alignments service or you have \
not installed pysam.'
    filename = request.args.get('file')
    if not filename:
        return "Please specify a filename."
    region = request.args.get('region')
    if not region:
        return "Please specify a region."

    args = []

    options = request.args.get("options")
    if options:
        args.append(unquote(options))

    reference = request.args.get('reference')
    if reference:
        reference = "static/alignments/refs/" + reference + ".fa"
        args.append("-T")
        args.append(reference)

    filename = "static/alignments/files/" + filename
    args.append(filename)
    args.append(region)

    try:
        return pysam.view(*args)
    except pysam.SamtoolsError as e:
        return e.value

@app.route('/ucsc')
def query_ucsc():
    if 'mysql.connector' not in sys.modules:
        return 'Either you have not enabled the UCSC library or you have \
not installed mysql-connector (pip install mysql-connector==2.1.4).'

    results = []

    def reg2bins(beg, end):
        bin_list = []
        end -= 1
        bin_list.append(0)
        for k in xrange(1 + (beg >> 26), 2 + (end >> 26)):
            bin_list.append(k)
        for k in xrange(9 + (beg >> 23), 10 + (end >> 23)):
            bin_list.append(k)
        for k in xrange(73 + (beg >> 20), 74 + (end >> 20)):
            bin_list.append(k)
        for k in xrange(585 + (beg >> 17), 586 + (end >> 17)):
            bin_list.append(k)
        for k in xrange(4681 + (beg >> 14), 4682 + (end >> 14)):
            bin_list.append(k)
        return bin_list

    db = request.args.get('db')
    table = request.args.get('table')
    genomic_range = request.args.get('genomic_range')

    ucsc_host = 'genome-mysql.soe.ucsc.edu'
    ucsc_user = 'genome'

    m = re.search('(chr\d+)', genomic_range)
    chrom = m.group(1)

    try:
        connection = mysql.connector.connect(host=ucsc_host, user=ucsc_user, database=db)
        cur = connection.cursor()

        cur.execute("SELECT * FROM information_schema.COLUMNS \
WHERE TABLE_NAME = %s AND COLUMN_NAME = 'bin' LIMIT 1", (table,))

        if cur.fetchone():
            m = re.search(chrom+':(\d+)-(\d*)', genomic_range)
            if m:
                start = int(m.group(1))
                end = int(m.group(2))

            bins = reg2bins(start, end)
            bin_str = '('+','.join(str(bin) for bin in bins)+')'

            cur.execute("SELECT * FROM "+table+" WHERE chrom = %s \
AND chromStart >= %s AND chromEnd <= %s \
AND bin in "+bin_str, (chrom, start, end))

        else:
            cur.execute("SELECT * FROM "+table+" WHERE chrom = %s", (chrom,))

        for row in cur.fetchall():
            row_dict = {}
            for name, value in zip(cur.description, row):
                row_dict[name[0]] = str(value)
            results.append(row_dict)

    except mysql.connector.Error, e:
        try:
            return "mysql Error [{}]: {}".format(e.args[0], e.args[1])
        except IndexError:
            return "mysql Error: {}".format(str(e))

    finally:
        cur.close()
        connection.close()

    return jsonify(results)

@app.before_request
def before_request():
    if app.config['USES_OAUTH'] and (not app.config['PUBLIC_DIR'] or \
            not os.path.exists('.'+app.config['PUBLIC_DIR']) or \
            not request.path.startswith(app.config['PUBLIC_DIR'])):
        auth = request.headers.get("Authorization", None)
	#print auth
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
