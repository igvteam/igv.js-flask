import sys
import os
from flask import request, url_for, Blueprint
from _config import basedir

err_message = 'Alignments service is enabled but pysam is not installed. Please \
install pysam (pip install pysam) if you wish to use the alignments service.'

try:
    import pysam
    from urllib import unquote
except ImportError:
    print err_message

alignments_blueprint = Blueprint('alignments', __name__, url_prefix='/alignments')

#alignments route
@alignments_blueprint.route('/')
def alignments():
    if 'pysam' not in sys.modules:
        return err_message

    filename = request.args.get('file')
    if not filename:
        return "Please specify a filename."
    region = request.args.get('region')
    if not region:
        return "Please specify a region."

    reference = request.args.get('reference')

    options = request.args.get("options")

    args = build_view_args(filename, region, reference, options)

    try:
        return pysam.view(*args)
    except pysam.SamtoolsError as e:
        return e.value

def build_view_args(filename, region, reference=None, options=None):
    args = []

    if options:
        args.append(unquote(options))

    if reference:
        reference = os.path.join(basedir,"static/alignments/refs/" + reference + ".fa")
        args.append("-T")
        args.append(reference)

    filename = os.path.join(basedir, "static/alignments/files/" + filename)
    args.append(filename)
    args.append(region)

    return args
