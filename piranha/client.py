from os import environ
import boto3


def get_client(service, region):
    if 'AWS_PROFILE' in environ:
        session = boto3.Session(profile_name=environ['AWS_PROFILE'])
    else:
        session = boto3.Session()
    return session.client(service, region_name=region)


def assume_role(account, role):
    sts = boto3.client('sts')
    response = sts.assume_role(RoleArn=f'arn:aws:iam::{account}:role/{role}',
                               RoleSessionName=f'{role}-session-{account}')
    if not response or not response['ResponseMetadata']['HTTPStatusCode'] == 200:
        raise Exception(f'could not assume {role} in {account}')
    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken'])
