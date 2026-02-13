from airflow.models import BaseOperator
from airflow.models import Variable
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowSkipException
from pathlib import Path


class ChangeVerifierOperator(BaseOperator):
    """
    Verifies whether the downloaded data has changed since the previous run.

    This operator compares the current file hash (stored by the downloader in Airflow's
    metadata DB) with the previous processed hash.

    Attributes:
        current_file (str | Path): Path to the newly downloaded data file.
        current_hash_variable_key (str): Variable key where downloader stores current hash.
        previous_hash_variable_key (str): Variable key where last processed hash is stored.

    Behavior:
        - First run (no previous hash): stores current hash as baseline and succeeds.
        - Subsequent runs:
            - If data has changed: updates previous hash and succeeds.
            - If data is unchanged: raises ValueError to stop downstream tasks.
    """

    @apply_defaults
    def __init__(
        self,
        current_file: str,
        current_hash_variable_key: str,
        previous_hash_variable_key: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.current_file: Path = Path(current_file)
        self.current_hash_variable_key: str = current_hash_variable_key
        self.previous_hash_variable_key: str = previous_hash_variable_key

    def execute(self, context: dict) -> None:
        """
        Executes the operator.

        - Reads current hash from the downloader's DB variable.
        - If no previous hash exists, creates a baseline from current hash.
        - If hashes differ, updates previous hash to current hash.
        - If hashes are identical, raises ValueError to stop downstream tasks.

        Args:
            context (dict): Airflow execution context (not used for comparison)

        Raises:
            ValueError: If current_file and previous_file have identical contents
        """
        if not self.current_file.exists():
            raise FileNotFoundError(f"Current file not found at {self.current_file}")

        current_hash = Variable.get(self.current_hash_variable_key, default_var=None)
        if not current_hash:
            raise ValueError(
                f"Current hash not found in Airflow Variable '{self.current_hash_variable_key}'. "
                "Ensure downloader task ran successfully before verifier."
            )

        previous_hash = Variable.get(self.previous_hash_variable_key, default_var=None)

        if previous_hash is None:
            self.log.info("No previous hash found. Treating current hash as baseline.")
            Variable.set(self.previous_hash_variable_key, current_hash)
            return

        self.log.info(f"Current file hash: {current_hash}")
        self.log.info(f"Previous file hash: {previous_hash}")

        if current_hash == previous_hash:
            raise AirflowSkipException("Data has not changed since last run")

        self.log.info("Data changed. Updating stored previous hash.")  # if the hashes are different
        Variable.set(self.previous_hash_variable_key, current_hash)