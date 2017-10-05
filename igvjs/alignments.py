import os
from flask import request, url_for, Blueprint
from igvjs._config import basedir

err_message = 'pysam is not installed. Please install pysam (pip install pysam) '\
'if you wish to use the alignments service.'

pysam_installed = True
try:
    import pysam
    from urllib import unquote
except ImportError:
    pysam_installed = False

alignments_blueprint = Blueprint('alignments', __name__, url_prefix='/alignments')

#alignments route
@alignments_blueprint.route('/', strict_slashes=False)
def alignments():
    if not pysam_installed:
        return err_message

    filename = request.args.get('file')

    if not filename:
        return "Please specify a filename."

    region = request.args.get('region')

    options = request.args.get("options")
    if options:
        options = options.split(",")

    # must specify region unless getting the header
    if not (region or '-H' in options):
        return "Please specify a region."

    reference = request.args.get('reference')

    args = build_view_args(filename, region, reference, options)

    try:
        return pysam.view(*args)
    except pysam.SamtoolsError as e:
        return e.value

def build_view_args(filename, region, reference=None, optionArray=None):
    args = []

    if optionArray:
        args.extend(optionArray)

    if reference:
        #reference = os.path.join(basedir,"static/alignments/refs/" + reference + ".fa")
        args.append("-T")
        args.append(reference)

    #filename = os.path.join(basedir, "static/alignments/files/" + filename)
    args.append(filename)

    if region:
        args.append(region)

    return args
