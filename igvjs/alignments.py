import os
from flask import request, url_for, Blueprint
from _config import basedir

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
@alignments_blueprint.route('/')
def alignments():
    if not pysam_installed:
        return err_message

    filename = request.args.get('file')

    if not filename:
        return "Please specify a filename."
    region = request.args.get('region')

  #  TODO -- enforce this unless getting header (-H)
  #  if not region:
  #      return "Please specify a region."

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
        optionArray = options.split(",")
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
