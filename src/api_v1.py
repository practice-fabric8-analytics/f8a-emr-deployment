import daiquiri
import logging

from flask import Flask, request, Blueprint
from flask_restful import Api, Resource

import src.config as config
from src.amazon_services import AmazonServices, AmazonEmr


daiquiri.setup(level=logging.DEBUG)
_logger = daiquiri.getLogger(__name__)

app = Flask(__name__)
api_bp = Blueprint('api',__name__)
api = Api(api_bp)


class AliveProbe(Resource):
    def get(self):
        _logger.info("alive:yes")
        return {"alive": "yes"}


class ReadinessProbe(Resource):
    def get(self):
        return {"status": "ok"}


class RunTrainingJob(Resource):
    def post(self):
        ecosystem = request.form.get('ecosystem')
        model = request.form.get('model')
        run_emr = AmazonEmr(config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_KEY_ID, 'us-east-1')
        run_emr.connect()
        resp = run_emr.run_training_job(model, ecosystem)
        return resp, 200


api.add_resource(ReadinessProbe, '/readiness')
api.add_resource(AliveProbe, '/liveness')
api.add_resource(RunTrainingJob, '/runjob', endpoint='runjob')
app.register_blueprint(api_bp, url_prefix='/api/v1')

if __name__=='__main__':
    app.run(debug=True)