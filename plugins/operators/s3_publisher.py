import os
from typing import Any, List, Optional
import boto3
from airflow.models import BaseOperator


class S3PublisherOperator(BaseOperator):
    """
    Custom Airflow operator to upload files or directories to an S3 bucket.

    This operator supports:
        - Single files
        - Entire directories (uploads recursively)
        - Optional S3 prefix for organizing files in the bucket
        - Lazy initialization of the S3 client for performance
    """

    def __init__(
        self,
        bucket_name : str,
        paths: List[str],
        s3_prefix: str = "",
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.bucket_name = bucket_name
        self.paths = paths
        self.s3_prefix = s3_prefix.strip("/")  # remove leading/trailing slashes
        self._s3_client: Optional[Any] = None  # will initialize lazily when needed

    def _get_s3_client(self) -> Any:
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

            if os.path.isfile(path):
                self._upload_file(s3, path)
            else:
                self._upload_directory(s3, path)

    def _upload_file(self, s3: Any, file_path: str) -> None:
        """
        Upload a single file to S3.

        Args:
            s3 (boto3.client): S3 client instance
            file_path (str): Local file path to upload
        """
        key = self._s3_key(file_path)
        self.log.info(f"Uploading {file_path} to s3://{self.bucket_name}/{key}")
        s3.upload_file(file_path, self.bucket_name, key)

    def _upload_directory(self, s3: Any, dir_path: str) -> None:
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
                self.log.info(f"Uploading {full_path} to s3://{self.bucket_name}/{key}")
                s3.upload_file(full_path, self.bucket_name, key)

    def _s3_key(self, path: str, base_path: Optional[str] = None) -> str:
        """
        Compute the S3 key (path) for a given local file.

        If base_path is provided, the key is the relative path from base_path,
        prefixed with s3_prefix if set. Otherwise, the key is just the file name,
        prefixed with s3_prefix if set.

        Args:
            path (str): Full path to the local file
            base_path (str, optional): Base directory for relative path computation

        Returns:
            str: S3 key (path in the S3 bucket)
        """
        if base_path:
            relative = os.path.relpath(path, base_path)
        else:
            relative = os.path.basename(path)

        if self.s3_prefix:
            return f"{self.s3_prefix}/{relative}"
        return relative