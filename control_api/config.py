from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict, Any


class AppSettings(BaseSettings):
    aws_bucket: str = Field(env='AWS_STORAGE_BUCKET_NAME')

    # admin_email: str = Field("admin@example.com", env='ADMIN_EMAIL')
    # items_per_user: int = Field(100, env='ITEMS_PER_USER')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'


settings = AppSettings()
