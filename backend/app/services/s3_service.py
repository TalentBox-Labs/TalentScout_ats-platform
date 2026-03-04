"""
AWS S3 service for file storage and retrieval.
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, Dict, Any
import uuid
from urllib.parse import quote

from app.config import settings


class S3Service:
    """Service for managing file uploads and downloads to/from AWS S3."""

    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.s3_bucket_name

        # Initialize S3 client if credentials are available
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region
                )
            except Exception as e:
                print(f"Failed to initialize S3 client: {str(e)}")
        else:
            print("AWS S3 credentials not configured, S3 functionality disabled")

    def is_enabled(self) -> bool:
        """Check if S3 service is properly configured."""
        return self.s3_client is not None

    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename for S3 storage."""
        if not original_filename:
            return f"{uuid.uuid4()}.bin"

        file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
        unique_id = uuid.uuid4()

        if file_extension:
            return f"{unique_id}.{file_extension}"
        else:
            return str(unique_id)

    def upload_file(self, file_content: bytes, key: str, content_type: str = None,
                   metadata: Dict[str, str] = None) -> Optional[str]:
        """
        Upload a file to S3.

        Args:
            file_content: File content as bytes
            key: S3 object key (path)
            content_type: MIME content type
            metadata: Additional metadata

        Returns:
            S3 URL if successful, None otherwise
        """
        if not self.is_enabled():
            print("S3 service not enabled")
            return None

        try:
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': key,
                'Body': file_content,
                'ACL': 'private'  # Files are private, accessed via signed URLs
            }

            if content_type:
                upload_params['ContentType'] = content_type

            if metadata:
                upload_params['Metadata'] = metadata

            # Upload file
            self.s3_client.put_object(**upload_params)

            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{quote(key)}"

            return s3_url

        except ClientError as e:
            print(f"S3 upload failed: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error during S3 upload: {str(e)}")
            return None

    def download_file(self, key: str) -> Optional[bytes]:
        """
        Download a file from S3.

        Args:
            key: S3 object key

        Returns:
            File content as bytes if successful, None otherwise
        """
        if not self.is_enabled():
            print("S3 service not enabled")
            return None

        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                print(f"File not found in S3: {key}")
            else:
                print(f"S3 download failed: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error during S3 download: {str(e)}")
            return None

    def delete_file(self, key: str) -> bool:
        """
        Delete a file from S3.

        Args:
            key: S3 object key

        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            print("S3 service not enabled")
            return False

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True

        except ClientError as e:
            print(f"S3 delete failed: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error during S3 delete: {str(e)}")
            return False

    def generate_presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary access to a private S3 object.

        Args:
            key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)

        Returns:
            Presigned URL if successful, None otherwise
        """
        if not self.is_enabled():
            print("S3 service not enabled")
            return None

        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            return url

        except ClientError as e:
            print(f"Failed to generate presigned URL: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error generating presigned URL: {str(e)}")
            return None

    def get_file_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a file in S3.

        Args:
            key: S3 object key

        Returns:
            File metadata if successful, None otherwise
        """
        if not self.is_enabled():
            print("S3 service not enabled")
            return None

        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return {
                'key': key,
                'size': response.get('ContentLength', 0),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag'),
                'metadata': response.get('Metadata', {})
            }

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                print(f"File not found in S3: {key}")
            else:
                print(f"Failed to get file info: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error getting file info: {str(e)}")
            return None


# Global S3 service instance
s3_service = S3Service()