from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowSkipException
from pathlib import Path
import hashlib
import shutil


class ChangeVerifier(BaseOperator):
    """
    Verifies whether the downloaded data has changed since the previous run.

    This operator compares a "current" data file (e.g., just downloaded phishing feed)
    with a "previous" data file (from the last DAG run). If the content has changed,
    it updates the previous file to the current one. If no previous file exists, it
    creates it as a baseline. If the data is unchanged, the operator raises a ValueError
    to prevent unnecessary downstream processing.

    Attributes:
        current_file (str | Path): Path to the newly downloaded data file.
        previous_file (str | Path): Path to the data file from the previous DAG run.

    Behavior:
        - First run (previous file missing): creates previous_file as baseline and succeeds.
        - Subsequent runs:
            - If data has changed: updates previous_file and succeeds.
            - If data is unchanged: raises ValueError to stop downstream tasks.
    """

    @apply_defaults
    def __init__(
        self,
        current_file: str,
        previous_file: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.current_file = Path(current_file)
        self.previous_file = Path(previous_file)

    def _hash(self, path: Path) -> str:
        """
        Computes the MD5 hash of a file.

        Args:
            path (Path): Path to the file to hash

        Returns:
            str: Hexadecimal MD5 hash of the file contents
        """
        h = hashlib.md5()
        with open(path, "rb") as f:  # opens the file in binary mode (works for any file type)
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)  # feed each chunk to the hash
        return h.hexdigest()  # converts internal binary hash to a readable string

    def execute(self, context) -> None:
        """
        Executes the operator.

        - If previous_file does not exist, copies current_file to previous_file.
        - If files differ, updates previous_file to match current_file.
        - If files are identical, raises ValueError to stop downstream tasks.

        Args:
            context (dict): Airflow execution context (not used for comparison)

        Raises:
            ValueError: If current_file and previous_file have identical contents
        """
        if not self.previous_file.exists():
            self.log.info("No previous file found. Treating current file as new data.")
            shutil.copy(self.current_file, self.previous_file)  # creates previous file from current one (creates baseline for next run)
            self.log.info(f"Baseline file created at {self.previous_file}.")
            return

        current_hash = self._hash(self.current_file)
        previous_hash = self._hash(self.previous_file)
        self.log.info(f"Current file hash: {current_hash}")
        self.log.info(f"Previous file hash: {previous_hash}")

        if current_hash == previous_hash:
            raise AirflowSkipException("Data has not changed since last run")

        self.log.info("Data changed. Updating previous file.")  # if the hashes are different
        shutil.copy(self.current_file, self.previous_file)  # overwrites previous file in this case
