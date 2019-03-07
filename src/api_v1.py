"""Defines rest API for emr deployment service."""

import daiquiri
import logging
import os

from flask import Flask, Blueprint, request
from flask_restful import Api, Resource
from flask.json import jsonify

import src.config as config
from src.exceptions import HTTPError
from fabric8a_auth.auth import login_required
from fabric8a_auth.auth import AuthError
from src.trained_model_details import trained_model_details
from rudra.utils.validation import check_field_exists
from rudra.deployments.emr_scripts.pypi_emr import PyPiEMR
from rudra.deployments.emr_scripts.maven_emr import MavenEMR
from rudra.deployments.emr_scripts.npm_emr import NpmEMR


daiquiri.setup(level=os.environ.get('FLASK_LOGGING_LEVEL', logging.INFO))
_logger = daiquiri.getLogger(__name__)

app = Flask(__name__)
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

emr_instances = {
    'maven': MavenEMR,
    'pypi': PyPiEMR,
    'npm': NpmEMR
}


class AliveProbe(Resource):
    """Check alive probe."""

    def get(self):
        """GET call to check liveness."""
        _logger.info("alive:yes")
        return {"alive": "yes"}


class ReadinessProbe(Resource):
    """Check readiness probe."""

    @staticmethod
    def get():
        """GET call to check readiness."""
        return {"status": "ok"}


class RunTrainingJob(Resource):
    """API for retraining purpose."""

    method_decorators = [login_required]

    @staticmethod
    def post():
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
        return status


class TrainedModelDetails(Resource):
    """Get call for fetching trained model details."""

    method_decorators = [login_required]

    @staticmethod
    def post():
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
        return output


api.add_resource(ReadinessProbe, '/readiness')
api.add_resource(AliveProbe, '/liveness')
api.add_resource(RunTrainingJob, '/runjob', endpoint='runjob')
api.add_resource(TrainedModelDetails, '/versions', endpoint='versions')
app.register_blueprint(api_bp, url_prefix='/api/v1')


@api_bp.errorhandler(AuthError)
def api_401_handler(err):
    """Handle AuthError Exceptions."""
    return jsonify(error=err.error), err.status_code


if __name__ == '__main__':
    app.run(debug=True)
