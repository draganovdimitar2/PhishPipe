import requests
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.models import Variable
import hashlib
import os


class PhishingGetterOperator(BaseOperator):
    """
    Downloads phishing email addresses from a public feed, writes the
    cleaned content to a local file, and stores the file hash in Airflow
    metadata variables.

    This operator is designed to be the first task in the phishing DAG.
    It fetches a line-based feed, removes comments/blank lines, writes
    normalized lines to ``output_path``, and computes an MD5 hash from the
    exact bytes written to disk. The resulting hash is persisted under
    ``hash_variable_key`` so downstream tasks can compare dataset versions
    without reopening and hashing files again.

    Attributes:
        output_path (str): Path where the cleaned feed will be saved.
        url (str): URL of the phishing feed to download.
        hash_variable_key (str): Airflow Variable key used to store
            the current downloaded file hash.

    Behavior:
        - Downloads data from the specified URL using HTTP GET.
        - Ensures the output directory exists.
        - Skips lines starting with "#" or empty lines.
        - Writes normalized lines (``line + "\\n"``) to the output file.
        - Computes MD5 incrementally from the same normalized lines.
        - Stores the computed hash in an Airflow Variable.
        - Returns the output file path after completion.
    """

    @apply_defaults
    def __init__(
            self,
            output_path: str,
            url: str,
            hash_variable_key: str,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.output_path: str = output_path
        self.url: str = url
        self.hash_variable_key: str = hash_variable_key

    def execute(self, context: dict) -> str:
        """
        Executes the download + clean + hash + persist flow.

        Steps:
            1. Logs the download start.
            2. Performs an HTTP GET request to fetch the data.
            3. Raises an exception if the request fails.
            4. Creates the output directory if it does not exist.
            5. Removes comment lines and empty lines from the feed.
            6. Writes normalized lines to the output file.
            7. Builds an MD5 hash from the same normalized lines.
            8. Saves the hash using ``Variable.set(hash_variable_key, hash)``.
            9. Logs completion and returns the output file path.

        Args:
            context (dict): Airflow execution context (not used in this operator).

        Returns:
            str: Path to the output file where the feed has been saved.

        Raises:
            requests.HTTPError: If the HTTP request to the feed fails.
            OSError: If the output file cannot be written.
            airflow.exceptions.AirflowException: If Airflow Variable
                persistence fails (e.g., invalid Fernet configuration).
        """
        self.log.info(f"Downloading data from {self.url} ...")
        response = requests.get(self.url, timeout=30)
        response.raise_for_status()

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        hasher = hashlib.md5()
        with open(self.output_path, "w") as f:
            for line in response.text.splitlines():
                if line.startswith("#") or not line.strip():  # remove empty lines or lines starting with "#"
                    continue
                normalized_line = line + "\n"
                f.write(normalized_line)
                hasher.update(normalized_line.encode("utf-8"))

        current_hash = hasher.hexdigest()
        Variable.set(self.hash_variable_key, current_hash)
        self.log.info("Saved downloaded file hash in Airflow metadata DB variable '%s': %s", self.hash_variable_key, current_hash)

        self.log.info(f"Data written to {self.output_path}")
        return self.output_path