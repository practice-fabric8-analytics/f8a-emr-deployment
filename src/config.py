"""This file contains constants required for retraining purpose."""
import os

DEPLOYMENT_PREFIX = os.environ.get('DEPLOYMENT_PREFIX', 'dev')
AWS_S3_ACCESS_KEY_ID = os.environ.get('AWS_S3_ACCESS_KEY_ID', '')
AWS_S3_SECRET_KEY_ID = os.environ.get('AWS_S3_SECRET_ACCESS_KEY', '')
