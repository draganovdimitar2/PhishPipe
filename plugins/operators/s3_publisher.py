import os
import boto3
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from typing import List, Optional


class S3PublisherOperator(BaseOperator):
    """
    Custom Airflow operator to upload files or directories to an S3 bucket.

    This operator supports:
        - Single files
        - Entire directories (uploads recursively)
        - Optional S3 prefix for organizing files in the bucket
        - Lazy initialization of the S3 client for performance
    """

    @apply_defaults
    def __init__(
            self,
            bucket_name: str,
            paths: List[str],
            s3_prefix: str = "",
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.bucket_name: str = bucket_name
        self.paths: List[str] = paths
        self.s3_prefix: str = s3_prefix.strip("/")  # remove leading/trailing slashes
        self._s3_client: Optional[boto3.client] = None  # will initialize lazily when needed

    def _get_s3_client(self) -> boto3.client:
        """
        Lazily initialize the boto3 S3 client.
        This avoids creating the client during DAG parsing, which is good for performance.

        Returns:
            boto3.client: S3 client instance
        """
        if self._s3_client is None:
            self.log.info("Initializing S3 client")
            self._s3_client = boto3.client("s3")
        return self._s3_client

    def execute(self, context: dict) -> None:
        """
        Main execution method called by Airflow.

        Iterates over all paths and uploads each to S3:
            - Files are uploaded directly.
            - Directories are uploaded recursively.
            - Raises FileNotFoundError if a path does not exist.

        Args:
            context (dict): Airflow execution context
        """
        s3 = self._get_s3_client()

        for path in self.paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Path does not exist: {path}")

            if os.path.isfile(path):  # deside which function to use
                self._upload_file(s3, path)
            else:
                self._upload_directory(s3, path)

    def _upload_file(self, s3: boto3.client, file_path: str) -> None:
        """
        Upload a single file to S3.

        Args:
            s3 (boto3.client): S3 client instance
            file_path (str): Local file path to upload
        """
        key = self._s3_key(file_path)
        self.log.info("Uploading %s to s3://%s/%s", file_path, self.bucket_name, key)
        s3.upload_file(file_path, self.bucket_name, key)

    def _upload_directory(self, s3: boto3.client, dir_path: str) -> None:
        """
        Recursively upload all files in a directory to S3.

        Args:
            s3 (boto3.client): S3 client instance
            dir_path (str): Local directory path to upload
        """
        for root, _, files in os.walk(dir_path):
            for file in files:
                full_path = os.path.join(root, file)
                key = self._s3_key(full_path, base_path=dir_path)
                self.log.info("Uploading %s to s3://%s/%s", full_path, self.bucket_name, key)
                s3.upload_file(full_path, self.bucket_name, key)

    def _s3_key(self, path: str, base_path: Optional[str] = None) -> str:
        """
        Compute the S3 key (path) for a given local file.

        If a base_path is provided (for directory uploads), the key is relative to that path.
        Otherwise, just uses the file name.

        Args:
            path (str): Local file path
            base_path (str, optional): Base path for relative key computation

        Returns:
            str: Full S3 key including optional prefix
        """
        if base_path:
            relative = os.path.relpath(path, base_path)  # compute path relative to directory root
        else:
            relative = os.path.basename(path)  # use just the filename for single files

        return f"{self.s3_prefix}/{relative}" if self.s3_prefix else relative  # prepend prefix if specified
