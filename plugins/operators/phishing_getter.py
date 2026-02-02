import requests
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import os

class PhishingGetterOperator(BaseOperator):
    """
    Downloads phishing email addresses from a public feed and writes
    the content to a local file.
    
    Attributes:
        output_path (str): Path to save the downloaded data file
        url (str): URL of the phishing feed
    """

    @apply_defaults
    def __init__(self, output_path: str, url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_path = output_path
        self.url = url

    def execute(self, context):
        self.log.info(f"Downloading data from {self.url} ...")
        response = requests.get(self.url)
        response.raise_for_status()

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, "w") as f:
            f.write(response.text)

        self.log.info(f"Data written to {self.output_path}")
        return self.output_path
