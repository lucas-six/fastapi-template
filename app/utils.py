"""Utilities."""

import os

from redis import Redis
from types_boto3_s3.client import S3Client


async def pid_str() -> str:
    return f'\033[0;34m{os.getpid()}\033[0m'


def get_file_url_from_s3(
    s3_client: S3Client,
    bucket_name: str,
    bucket_key: str,
    expire: int = 3600,
    redis_client: Redis | None = None,
    cache_key: str = '',
) -> str:
    """Get file from S3."""
    if redis_client and expire > 0 and cache_key:
        s3_presigned_url = redis_client.hget(cache_key, bucket_key)
        if s3_presigned_url:
            return s3_presigned_url

    s3_presigned_url = s3_client.generate_presigned_url(
        'get_object', Params={'Bucket': bucket_name, 'Key': bucket_key}, ExpiresIn=expire
    )

    # Cache the presigned URL
    if expire > 0 and redis_client:
        redis_client.hset(cache_key, bucket_key, s3_presigned_url)
        redis_client.expire(cache_key, expire)

    return s3_presigned_url
