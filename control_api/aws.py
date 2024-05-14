import boto3
from config import settings


s3 = boto3.client(
    service_name='s3',
    endpoint_url='https://s3.ru-1.storage.selcloud.ru'
)


class AWSService:

    @staticmethod
    def download_file(file_s3_url: str, path_to_save: str):

        get_object_response = s3.get_object(Bucket=settings.aws_bucket, Key=file_s3_url)
        file_content = get_object_response['Body'].read()

        with open(path_to_save, 'wb') as file:
            file.write(file_content)

