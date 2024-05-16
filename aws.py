import os
from urllib.parse import urlparse

import boto3
from config import settings

#
# s3 = boto3.client(
#     service_name='s3',
#     endpoint_url='https://s3.ru-1.storage.selcloud.ru'
# )

session = boto3.Session(
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

s3 = session.client('s3', endpoint_url='https://s3.ru-1.storage.selcloud.ru')


class AWSService:

    @staticmethod
    def download_file(file_s3_url: str, path_to_save: str):
        parsed_url = urlparse(file_s3_url)
        file_s3_key = parsed_url.path.lstrip('/')
        print(f"Downloading {file_s3_key} from {file_s3_url}")
        get_object_response = s3.get_object(Bucket=settings.aws_storage_bucket_name, Key=file_s3_key)

        file_content = get_object_response['Body'].read()

        os.makedirs(os.path.dirname(path_to_save), exist_ok=True)

        with open(path_to_save, 'wb') as file:
            file.write(file_content)

        print(f"File saved to {path_to_save}")
