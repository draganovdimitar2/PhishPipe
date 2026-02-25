import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from plugins.operators.phishing_getter import PhishingGetterOperator
import requests


class TestPhishingGetterOperator(unittest.TestCase):
    @patch("plugins.operators.phishing_getter.requests.get")
    def test_http_error_raises(self, mock_get):
        """Test when request returns a non-200 status code."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")

        mock_get.return_value = mock_response

        operator = PhishingGetterOperator(
            task_id="phishing",
            output_path="output.txt",
            url="http://fake-url.com",
            hash_variable_key="hash_key"
        )

        with self.assertRaises(requests.HTTPError):  # has to raise HTTPError
            operator.execute(context={})

    @patch("plugins.operators.phishing_getter.Variable.set")
    @patch("plugins.operators.phishing_getter.requests.get")
    def test_execute_downloads_and_writes_file(self, mock_get, mock_variable_set):
        fake_response = MagicMock()  # make a mock obj of our response
        fake_response.text = """
# comment
test1@example.com

test2@example.com
"""
        fake_response.raise_for_status.return_value = None
        mock_get.return_value = fake_response

        output_file = Path("data/test_output.txt")

        operator = PhishingGetterOperator(
            task_id="test_task",
            output_path=str(output_file),
            url="http://fake-url.com",
            hash_variable_key="test_hash"
        )

        result = operator.execute(context={})

        self.assertTrue(output_file.exists())

        content = output_file.read_text()
        self.assertIn("test1@example.com", content)
        self.assertIn("test2@example.com", content)
        self.assertNotIn("#", content)

        mock_variable_set.assert_called_once()

        self.assertEqual(result, str(output_file))

        output_file.unlink()


if __name__ == "__main__":
    unittest.main()
