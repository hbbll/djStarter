from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import os


class MinioMediaStorage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        kwargs['endpoint_url'] = settings.AWS_S3_ENDPOINT_URL
        kwargs['access_key'] = settings.AWS_ACCESS_KEY_ID
        kwargs['secret_key'] = settings.AWS_SECRET_ACCESS_KEY
        kwargs['bucket_name'] = settings.AWS_STORAGE_BUCKET_NAME
        kwargs['region_name'] = 'us-east-1'
        kwargs['use_ssl'] = False
        kwargs['verify'] = settings.AWS_S3_VERIFY
        kwargs['default_acl'] = settings.AWS_DEFAULT_ACL
        super().__init__(*args, **kwargs)
