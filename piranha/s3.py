import json

import boto3
from botocore.exceptions import ClientError


def fetch(bucket, key):
    s3 = boto3.resource('s3')
    try:
        obj = s3.Object(bucket, key)
        return obj.get()['Body'].read().decode('utf-8')
    except ClientError:
        return None


def upload(bucket, key, data, content_type):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    bucket.put_object(Key=key, Body=data, ContentType=content_type)


def upload_file(bucket, key, file_path, content_type):
    with open(file_path, "rb") as fh:
        upload(bucket, key, fh.read(), content_type)


def fetch_json(bucket, key):
    data = fetch(bucket, key)
    if data:
        return json.loads(data)
    return None


def upload_json(bucket, key, data):
    upload(bucket, key, json.dumps(data), 'application/json')
