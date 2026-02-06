import requests
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import os


class PhishingGetterOperator(BaseOperator):
    """
    Downloads phishing email addresses from a public feed and writes
    the content to a local file.

    This operator fetches a CSV-style feed from a given URL, removes
    comment lines or empty lines, and writes the cleaned content to
    a specified local file path. It can be used as the first task in
    a pipeline to gather phishing email addresses for further processing.

    Attributes:
        output_path (str): Path where the cleaned feed will be saved.
        url (str): URL of the phishing feed to download.

    Behavior:
        - Downloads data from the specified URL using HTTP GET.
        - Ensures the output directory exists.
        - Skips lines starting with "#" or empty lines.
        - Writes the remaining lines to the output file.
        - Returns the output file path after completion.
    """

    @apply_defaults
    def __init__(
            self,
            output_path: str,
            url: str,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.output_path: str = output_path
        self.url: str = url

    def execute(self, context: dict) -> str:
        """
        Executes the operator to download and write the phishing feed.

        Steps:
            1. Logs the download start.
            2. Performs an HTTP GET request to fetch the data.
            3. Raises an exception if the request fails.
            4. Creates the output directory if it does not exist.
            5. Removes comment lines and empty lines from the feed.
            6. Writes the cleaned content to the output file.
            7. Logs completion and returns the output file path.

        Args:
            context (dict): Airflow execution context (not used in this operator).

        Returns:
            str: Path to the output file where the feed has been saved.

        Raises:
            requests.HTTPError: If the HTTP request to the feed fails.
            OSError: If the output file cannot be written.
        """
        self.log.info(f"Downloading data from {self.url} ...")
        response = requests.get(self.url, timeout=30)
        response.raise_for_status()

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, "w") as f:
            for line in response.text.splitlines():
                if line.startswith("#") or not line.strip():  # remove empty lines or lines starting with "#"
                    continue
                f.write(line + "\n")

        self.log.info(f"Data written to {self.output_path}")
        return self.output_path
