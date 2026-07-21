import os
from typing import Any, List, Optional
import boto3
from botocore.exceptions import ClientError

try:
    from airflow.models import BaseOperator
except (ImportError, ModuleNotFoundError):
    class BaseOperator:
        def __init__(self, *args: Any, **kwargs: Any):
            pass


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
        bucket_name: str,
        paths: List[str],
        s3_prefix: str = "",
        create_bucket_if_missing: bool = True,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.bucket_name = bucket_name
        self.paths = paths
        self.s3_prefix = s3_prefix.strip("/")  # remove leading/trailing slashes
        self.create_bucket_if_missing = create_bucket_if_missing
        self._s3_client: Optional[Any] = None  # will initialize lazily when needed

    def _get_s3_client(self) -> Any:
        """
        Lazily initialize the boto3 S3 client.
        This avoids creating the client during DAG parsing, which is good for performance.
        
        Supports LocalStack endpoint URL via AWS_S3_ENDPOINT_URL environment variable
        for local S3 mocking.

        Returns:
            boto3.client: S3 client instance
        """
        if self._s3_client is None:
            self.log.info("Initializing S3 client")
            endpoint_url = os.getenv("AWS_S3_ENDPOINT_URL")
            if endpoint_url:
                self.log.info(f"Using custom S3 endpoint: {endpoint_url}")
                self._s3_client = boto3.client("s3", endpoint_url=endpoint_url)
            else:
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

        if self.create_bucket_if_missing:
            self._ensure_bucket_exists(s3)

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

    def _ensure_bucket_exists(self, s3: Any) -> None:
        """
        Ensure the target S3 bucket exists before uploading.

        Args:
            s3 (boto3.client): S3 client instance
        """
        try:
            self.log.info(f"Checking whether S3 bucket exists: {self.bucket_name}")
            s3.head_bucket(Bucket=self.bucket_name)
            self.log.info(f"S3 bucket already exists: {self.bucket_name}")
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code in ("404", "NoSuchBucket", "NotFound"):
                self.log.info(f"Creating missing S3 bucket: {self.bucket_name}")
                create_kwargs = {"Bucket": self.bucket_name}
                region = os.getenv("AWS_DEFAULT_REGION")
                if region and region != "us-east-1":
                    create_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}
                s3.create_bucket(**create_kwargs)
            else:
                raise

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