"""Defines rest API for emr deployment service."""

import daiquiri
import logging
import os

from flask import Flask, request
from flask.json import jsonify
from flask_cors import CORS

import src.config as config
from src.exceptions import HTTPError
from fabric8a_auth.auth import AuthError
from src.trained_model_details import trained_model_details
from rudra.utils.validation import check_field_exists
from rudra.deployments.emr_scripts.pypi_emr import PyPiEMR
from rudra.deployments.emr_scripts.maven_emr import MavenEMR
from rudra.deployments.emr_scripts.npm_emr import NpmEMR


daiquiri.setup(level=os.environ.get('FLASK_LOGGING_LEVEL', logging.INFO))
_logger = daiquiri.getLogger(__name__)


app = Flask(__name__)
CORS(app)

emr_instances = {
    'maven': MavenEMR,
    'pypi': PyPiEMR,
    'npm': NpmEMR
}


@app.route('/api/v1/readiness')
def readiness():
    """Readiness probe."""
    return jsonify({"status": "ready"}), 200


@app.route('/api/v1/liveness')
def liveness():
    """Liveness probe."""
    return jsonify({}), 200


@app.route('/api/v1/runjob', methods=['POST'])
def run_training_job():
    """POST call for initiating retraining of models."""
    required_fields = ["data_version", "bucket_name", "github_repo", "ecosystem"]
    input_data = request.get_json()
    missing_fields = check_field_exists(input_data, required_fields)
    if missing_fields:
        raise HTTPError(400, "These field(s) {} are missing from input "
                             "data".format(missing_fields))
    if not input_data:
        raise HTTPError(400, "Expected JSON request")
    if type(input_data) != dict:
        raise HTTPError(400, "Expected dict of input parameters")
    input_data['environment'] = config.DEPLOYMENT_PREFIX
    ecosystem = input_data.get('ecosystem')
    emr_instance = emr_instances.get(ecosystem)
    if emr_instance:
        emr_instance = emr_instance()
        status = emr_instance.run_job(input_data)
    else:
        raise HTTPError(400, "Ecosystem {} not supported yet.".format(ecosystem))
    return jsonify(status), 200


@app.route('/api/v1/versions', methods=['POST'])
def version_details():
    """POST call to fetch model details."""
    required_fields = ["bucket_name", "ecosystem"]
    input_data = request.get_json()
    missing_fields = check_field_exists(input_data, required_fields)
    if missing_fields:
        raise HTTPError(400, "These field(s) {} are missing from input "
                             "data".format(missing_fields))
    if not input_data:
        raise HTTPError(400, "Expected JSON request")
    if type(input_data) != dict:
        raise HTTPError(400, "Expected dict of input parameters")
    bucket = input_data['bucket_name']
    ecosystem = input_data['ecosystem']
    output = trained_model_details(bucket, ecosystem)
    return jsonify(output), 200


@app.errorhandler(HTTPError)
def handle_error(e):  # pragma: no cover
    """Handle http error response."""
    return jsonify({
        "error": e.error
    }), e.status_code


@app.errorhandler(AuthError)
def api_401_handler(err):
    """Handle AuthError exceptions."""
    return jsonify(error=err.error), err.status_code


if __name__ == '__main__':
    app.run(debug=True)
