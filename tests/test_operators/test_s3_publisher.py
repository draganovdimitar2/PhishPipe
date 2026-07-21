import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from botocore.exceptions import ClientError

# Provide a dummy fcntl module on Windows so Airflow imports succeed during tests.
if sys.platform == "win32":
    fcntl = types.ModuleType("fcntl")
    fcntl.flock = lambda *args, **kwargs: None
    fcntl.lockf = lambda *args, **kwargs: None
    sys.modules["fcntl"] = fcntl

# Set Airflow environment variables before importing Airflow-dependent modules.
AIRFLOW_HOME = os.path.abspath("airflow_home")
os.makedirs(AIRFLOW_HOME, exist_ok=True)
os.makedirs(os.path.join(AIRFLOW_HOME, "logs"), exist_ok=True)
os.environ.setdefault("AIRFLOW_HOME", AIRFLOW_HOME)
os.environ.setdefault("AIRFLOW__CORE__BASE_LOG_FOLDER", os.path.join(AIRFLOW_HOME, "logs"))
db_path = os.path.abspath(
    os.path.join(AIRFLOW_HOME, "airflow.db")
).replace("\\", "/")

os.environ.setdefault(
    "AIRFLOW__CORE__SQL_ALCHEMY_CONN",
    f"sqlite:////{db_path}"
)

from plugins.operators.s3_publisher import S3PublisherOperator


class TestS3PublisherOperator(unittest.TestCase):
    def test_s3_key_with_prefix(self):
        """Test s3_key with prefix"""
        operator = S3PublisherOperator(
            task_id="upload",
            bucket_name="bucket",
            paths=[],
            s3_prefix="prefix"
        )

        key = operator._s3_key("file.txt")

        self.assertEqual(key, "prefix/file.txt")  # now the key to the obj in s3 should be `prefix/file.txt`

    @patch("plugins.operators.s3_publisher.boto3.client")
    def test_s3_client_initialized_once(self, mock_boto_client):
        """test that boto3.client() is called only once"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        operator = S3PublisherOperator(
            task_id="upload",
            bucket_name="bucket",
            paths=[]
        )

        operator._get_s3_client()
        operator._get_s3_client()

        mock_boto_client.assert_called_once_with("s3")

    @patch("plugins.operators.s3_publisher.boto3.client")
    def test_ensure_bucket_exists_creates_missing_bucket(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_s3.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}},
            "HeadBucket"
        )
        mock_boto_client.return_value = mock_s3

        operator = S3PublisherOperator(
            task_id="upload",
            bucket_name="missing-bucket",
            paths=["file.txt"]
        )

        operator._ensure_bucket_exists(mock_s3)

        mock_s3.create_bucket.assert_called_once_with(Bucket="missing-bucket")

    @patch("plugins.operators.s3_publisher.boto3.client")
    def test_path_does_not_exist_raises(self, mock_boto_client):
        """Test with some fake path and it should raise an error"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        operator = S3PublisherOperator(
            task_id="upload",
            bucket_name="my-bucket",
            paths=["fake_path.txt"],
            create_bucket_if_missing=False
        )

        with self.assertRaises(FileNotFoundError):
            operator.execute(context={})

    @patch("plugins.operators.s3_publisher.boto3.client")
    def test_upload_directory(self, mock_boto_client):
        """Testing with directory path not single file."""
        base_dir = Path("test_dir")
        base_dir.mkdir()  # some fake dir
        file1 = base_dir / "a.txt"  # fake files inside it
        file2 = base_dir / "b.txt"
        file1.write_text("a")
        file2.write_text("b")

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        operator = S3PublisherOperator(
            task_id="upload",
            bucket_name="my-bucket",
            paths=[str(base_dir)]
        )

        operator.execute(context={})

        self.assertEqual(mock_s3.upload_file.call_count, 2)

        file1.unlink()  # remove the files and dir
        file2.unlink()
        base_dir.rmdir()

    @patch("plugins.operators.s3_publisher.boto3.client")  # mock the s3 client
    def test_upload_single_file(self, mock_boto_client):
        """Testing with single file path."""
        test_file = Path("file.txt")  # some mock file is created
        test_file.write_text("data")

        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        operator = S3PublisherOperator(
            task_id="upload",
            bucket_name="my-bucket",
            paths=[str(test_file)],
            s3_prefix="test"
        )

        operator.execute(context={})

        mock_s3.upload_file.assert_called_once()

        test_file.unlink()


if __name__ == "__main__":
    unittest.main()
