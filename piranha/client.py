from os import environ
import boto3


def get_client(service, region):
    if 'AWS_PROFILE' in environ:
        session = boto3.Session(profile_name=environ['AWS_PROFILE'])
    else:
        session = boto3.Session()
    return session.client(service, region_name=region)
