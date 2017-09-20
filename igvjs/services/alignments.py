import sys
from flask import request
from igvjs.services import services_blueprint

#alignments route
@services_blueprint.route('/alignments')
def alignments():
    if 'pysam' not in sys.modules:
        if services_blueprint.alignments_enabled:
            try:
                import pysam
                from urllib import unquote
            except ImportError:
                return 'Alignments service is enabled but pysam is not installed. Please \
install pysam (pip install pysam) if you wish to use the alignments service.'
        else:
            return 'You have not enabled the alignments service. Please enable \
it in _config.py and also make sure to install pysam (pip install pysam).'

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
