from flask import Blueprint

services_blueprint = Blueprint('services', __name__)

# let blueprint know which services are enabled
@services_blueprint.record
def record_services(setup_state):
    config = setup_state.app.config;
    services_blueprint.alignments_enabled = config['ENABLE_ALIGNMENT_SERVICE']
    services_blueprint.ucsc_enabled = config['ENABLE_UCSC_SERVICE']

import alignments
import ucsc
