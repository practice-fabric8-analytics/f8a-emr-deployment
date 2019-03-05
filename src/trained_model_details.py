"""Function to return data set versions and trained model details."""

import src.config as config

from rudra.data_store.aws import AmazonS3


def trained_model_details(bucket_name, ecosystem):
    """Return  precision and recall for each version."""
    s3 = AmazonS3(bucket_name=bucket_name, aws_access_key_id=config.AWS_S3_ACCESS_KEY_ID,
                  aws_secret_access_key=config.AWS_S3_SECRET_KEY_ID)
    s3.connect()
    prefix = "{}/{}/".format(ecosystem, config.DEPLOYMENT_PREFIX)
    versions = s3.list_bucket_objects(prefix=prefix)
    versions = [val.key for val in versions]
    version_details = dict()
    for ver in versions:
        if "intermediate-model/hyperparameters" in ver:
            version = ver.split('/')[-3]
            if s3.object_exists(ver):
                version_info = s3.read_json_file(ver)
            version_details[version] = version_info
    return version_details
