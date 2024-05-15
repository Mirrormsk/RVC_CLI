from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict, Any


class AppSettings(BaseSettings):
    aws_access_key_id: str = Field(env='AWS_ACCESS_KEY_ID')
    aws_secret_access_key: str = Field(env='AWS_SECRET_ACCESS_KEY')
    aws_storage_bucket_name: str = Field(env='AWS_STORAGE_BUCKET_NAME')
    aws_s3_endpoint_url: Optional[str] = Field(default=None, env='AWS_S3_ENDPOINT_URL')
    aws_s3_custom_domain: Optional[str] = Field(default=None, env='AWS_S3_CUSTOM_DOMAIN')
    aws_s3_use_ssl: bool = Field(default=True, env='AWS_S3_USE_SSL')
    queue_name: str = Field(env='QUEUE_NAME')
    rmq_connection_url: str = Field(env='RMQ_CONNECTION_URL')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'



settings = AppSettings()
