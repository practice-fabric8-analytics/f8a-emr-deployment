import boto3
import daiquiri
import logging
import botocore
import os

import src.config as config
# from hpf_insights.pypi.pypi_emr import PyPiEmr
daiquiri.setup(level=logging.DEBUG)
_logger = daiquiri.getLogger(__name__)


class AmazonServices:
    """Class that encapsulates emr instance creation code.
    """

    def create_client(self, client_type, region_name=None):
        """Create client for aws operations"""
        if region_name is None:
            try:
                aws_client = boto3.client(client_type,
                                         aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                                         aws_secret_access_key=config.AWS_SECRET_KEY_ID,
                                         region_name='us-east-1')
            except Exception:
                _logger.exception("Error while creating client")
                raise
        else:
            try:
                aws_client = boto3.client(client_type,
                                         aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                                         aws_secret_access_key=config.AWS_SECRET_KEY_ID,
                                         region_name=region_name)
            except Exception:
                _logger.exception("Error while creating client")
                raise

        return aws_client

    def upload_to_s3(self, input_file_path, bucket_name, input_file_key):
        """Function to upload files to amazon s3"""
        s3_client = self.create_client('s3')
        s3_client.upload_file(input_file_path, bucket_name, input_file_key)

    def submit_job(self, client, job_url, bootstrap_url):
        """Function to create a EMR instance and run the job to retrain the ml model."""
        log_uri = 's3://ssamal-anchor-packages/logs'
        # s3_uri = 's3://ssamal-anchor-packages/hello.py'
        # s3_bootstrap_uri = 's3://ssamal-anchor-packages/bootstrap.sh'
        # emr_client = self.create_client('emr')
        response = client.run_job_flow(
            Name='sunil-test',
            LogUri=log_uri,
            ReleaseLabel='emr-5.10.0',
            Instances={
                'KeepJobFlowAliveWhenNoSteps': False,
                'TerminationProtected': False,
                'Ec2SubnetId': 'subnet-50271f16',
                'Ec2KeyName': 'Zeppelin2Spark',
                'InstanceGroups': [
                    {
                        'Name': 'sunil-test',
                        'InstanceRole': 'MASTER',
                        'InstanceType': 'm3.xlarge',
                        'InstanceCount': 1,
                        'Configurations': [
                            {
                                    "Classification": "spark-env",
                                "Properties": {},
                                "Configurations": [
                                    {
                                        "Classification": "export",
                                        "Configurations": [],
                                        "Properties": {
                                            "LC_ALL": "en_US.UTF-8",
                                            "LANG": "en_US.UTF-8",
                                            "AWS_S3_ACCESS_KEY_ID": 'AKIAJCUPZHEVTJPVUXNA',
                                            "AWS_S3_SECRET_KEY_ID": 'LM0ksbxa7CX0QAVu9qG6n+0dbsQNqLFtDiOsH5DE'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ],
            },
            BootstrapActions=[
                {
                    'Name': 'Metadata setup',
                    'ScriptBootstrapAction': {
                        'Path': bootstrap_url
                    }
                }
            ],
            Steps=[
                {
                    'Name': 'setup - copy files',
                    'ActionOnFailure': 'TERMINATE_CLUSTER',
                    'HadoopJarStep': {
                        'Jar': 'command-runner.jar',
                        'Args': ['aws', 's3', 'cp', job_url, '/home/hadoop/tmp']
                    }
                },
                {
                    'Name': 'Run program',
                    'ActionOnFailure': 'TERMINATE_CLUSTER',
                    'HadoopJarStep': {
                        'Jar': 'command-runner.jar',
                        'Args': ['/bin/sh', '-c',
                                 "PYTHONPATH='/home/hadoop' python3.6"
                                 " /home/hadoop/tmp/hello.py"]
                    }
                }
            ],
            Applications=[{'Name': 'MXNet'}],
            VisibleToAllUsers=True,
            JobFlowRole='EMR_EC2_DefaultRole',
            ServiceRole='EMR_DefaultRole'
        )
        output = {}
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:

            output['training_job_id'] = response.get('JobFlowId')
            output['status'] = 'work_in_progress'
            output[
                'status_description'] = "The training is in progress. Please check the given " \
                                        "training job after some time."
        else:
            output['training_job_id'] = "Error"
            output['status'] = 'Error'
            output['status_description'] = "Error! The job/cluster could not be created!"
            _logger.debug(response)

        return output

    def run_emr_job(self, model, ecosytem, environment=None):
        if model == 'hpf_insights':
            if ecosytem == 'pypi':
                pyemr = PyPiEmr()
                emr_client = self.create_client('emr')
                resp = pyemr.submit_pypi_job(emr_client, config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_KEY_ID)

        return resp

class NotFoundAccessKeySecret(Exception):
    """Exception for invalid AWS secret/key."""

    def __init__(self):
        """Initialize the Exception."""
        self.message = ("AWS configuration not provided correctly, "
                        "both key id and key is needed")
        super().__init__(self.message)

class AmazonEmr():
    """Basic interface to the Amazon EMR."""

    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None,
                 region_name=None):
        """Initialize object, setup connection to the AWS S3."""
        self._emr = None

        self.region_name = os.getenv(
            'AWS_S3_REGION') or region_name or self._DEFAULT_REGION_NAME
        self._aws_access_key_id = os.getenv(
            'AWS_S3_ACCESS_KEY_ID') or aws_access_key_id
        self._aws_secret_access_key = \
            os.getenv('AWS_S3_SECRET_ACCESS_KEY') or aws_secret_access_key

    def connect(self):
        """Connect to the emr instance."""
        try:
            session = boto3.session.Session(aws_access_key_id=self._aws_access_key_id,
                                            aws_secret_access_key=self._aws_secret_access_key,
                                            region_name=self.region_name)

            self._emr = session.client('emr', config=botocore.client.Config(
                    signature_version='s3v4'))
            _logger.info("Connecting to the emr")
        except Exception as exc:
            _logger.info(
                "An Exception occurred while establishing a AmazonEMR connection {}"
                .format(str(exc)))

    def run_training_job(self, model=None, ecosystem=None, environment=None, bucket_name=None):
        """Function to submit job for training model."""
        _logger.info("model {}".format(model))
        try:
            if model == 'hpf_insights':
                if ecosystem == 'pypi':
                    _logger.info("I am here 2")
                    pyemr = PyPiEmr()
                    _logger.info("I am here 2")
                    resp = pyemr.submit_pypi_job(self._emr, config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_KEY_ID)
                    _logger.info("resp {}".format(resp))
                    return resp
        except Exception as exc:
            _logger.info("An exception occurred while submitting job to emr {}".format(str(exc)))