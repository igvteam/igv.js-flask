from flask import Flask
from flask_compress import Compress

app = Flask(__name__)

# get config values from _config.py
app.config.from_pyfile('_config.py')

Compress(app)

if app.config['ENABLE_CORS_REQUESTS']:
    from flask_cors import CORS, cross_origin
    CORS(app)

from igvjs.main import igvjs_blueprint
from igvjs.ucsc import ucsc_blueprint
from igvjs.alignments import alignments_blueprint

app.register_blueprint(igvjs_blueprint)
app.register_blueprint(alignments_blueprint)
app.register_blueprint(ucsc_blueprint)
