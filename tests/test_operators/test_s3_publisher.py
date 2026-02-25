import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
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

    def test_path_does_not_exist_raises(self):
        """Test with some fake path and it should raise an error"""
        operator = S3PublisherOperator(
            task_id="upload",
            bucket_name="my-bucket",
            paths=["fake_path.txt"]  # fake path
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
