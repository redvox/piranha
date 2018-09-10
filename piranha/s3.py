import json

import boto3
from botocore.exceptions import ClientError


def get_data(bucket, key):
    s3 = boto3.resource('s3')
    try:
        obj = s3.Object(bucket, key)
        return obj.get()['Body'].read().decode('utf-8')
    except ClientError:
        return None


def upload_data(bucket, key, data, content_type='application/json'):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    bucket.put_object(Key=key, Body=data, ContentType=content_type)


def get_json(bucket, key):
    data = get_data(bucket, key)
    if data:
        return json.loads(data)
    return None


def upload_json(bucket, key, data, content_type='application/json'):
    upload_data(bucket, key, json.dumps(data), content_type)
