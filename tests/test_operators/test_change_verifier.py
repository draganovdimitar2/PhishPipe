import unittest
from plugins.operators.change_verifier import ChangeVerifierOperator
from unittest.mock import patch
from pathlib import Path
from airflow.exceptions import AirflowSkipException


class TestChangeVerifierOperator(unittest.TestCase):

    def test_current_file_does_not_exists_raises_file_not_found_error(self):
        """“Verifies that If the file does not exist, the operator fails immediately.”"""
        path_that_doesnt_exist = "fake_path/file_that_doesnt_exist.txt"  # some fake path
        operator = ChangeVerifierOperator(
            task_id='test_change_verifier',
            current_file=path_that_doesnt_exist,
            current_hash_variable_key="current_hash_variable_key",
            previous_hash_variable_key="previous_hash_variable_key"
        )
        with self.assertRaises(FileNotFoundError):  # it should raise this error
            operator.execute(context={})

    @patch("plugins.operators.change_verifier.Variable.get")
    def test_current_hash_not_available_raises_value_error(self, mock_get):
        """Test when a current hash is missing, will it raise a ValueError"""
        test_file = Path("data.txt")  # mock some file
        test_file.write_text("dummy")

        mock_get.return_value = None  # current hash missing

        operator = ChangeVerifierOperator(
            task_id="verify",
            current_file=str(test_file),
            current_hash_variable_key="current",
            previous_hash_variable_key="previous"
        )
        with self.assertRaises(ValueError):
            operator.execute(context={})

        test_file.unlink()

    @patch("plugins.operators.change_verifier.Variable.set")
    @patch("plugins.operators.change_verifier.Variable.get")
    def test_first_run_sets_baseline(self, mock_get, mock_set):
        """Test previous hash is None and setting the baseline"""
        test_file = Path("data.txt")
        test_file.write_text("dummy")

        mock_get.side_effect = ["currenthash", None]  # now previous_hash is None

        operator = ChangeVerifierOperator(
            task_id="verify",
            current_file=str(test_file),
            current_hash_variable_key="current",  # we don't need the actual value of this
            previous_hash_variable_key="previous"
        )

        operator.execute(context={})

        mock_set.assert_called_once_with("previous", "currenthash")
        test_file.unlink()

    @patch("plugins.operators.change_verifier.Variable.get")
    def test_skip_if_hash_unchanged(self, mock_get):
        """Test when hashes are the same"""
        test_file = Path("data.txt")
        test_file.write_text("dummy")

        mock_get.side_effect = ["samehash", "samehash"]

        operator = ChangeVerifierOperator(
            task_id="verify",
            current_file=str(test_file),
            current_hash_variable_key="current",
            previous_hash_variable_key="previous"
        )

        with self.assertRaises(AirflowSkipException):
            operator.execute(context={})

        test_file.unlink()

    @patch("plugins.operators.change_verifier.Variable.set")
    @patch("plugins.operators.change_verifier.Variable.get")
    def test_hash_changed_updates_previous_hash(self, mock_get, mock_set):
        """Test when hash is changed whether previous hash is updated"""
        test_file = Path("data.txt")
        test_file.write_text("dummy")

        mock_get.side_effect = ["currenthash", "previoushash"]  # current != previous

        operator = ChangeVerifierOperator(
            task_id="verify",
            current_file=str(test_file),
            current_hash_variable_key="current",
            previous_hash_variable_key="previous"
        )

        operator.execute(context={})

        mock_set.assert_called_once_with("previous", "currenthash")
        test_file.unlink()


if __name__ == "__main__":
    unittest.main()
