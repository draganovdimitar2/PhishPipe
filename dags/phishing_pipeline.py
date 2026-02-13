from datetime import datetime
from airflow import DAG
from operators.phishing_getter import PhishingGetterOperator
from operators.change_verifier import ChangeVerifierOperator
from operators.s3_publisher import S3PublisherOperator
from config import (
    PHISHING_FEED_URL,
    PHISHING_CURRENT_FILE_PATH,
    PHISHING_CURRENT_HASH_VARIABLE_KEY,
    PHISHING_PREVIOUS_HASH_VARIABLE_KEY,
)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 2, 2),
    'retries': 1
}

with DAG(
        dag_id='phishing_pipeline',
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False
) as dag:
    downloader = PhishingGetterOperator(
        task_id='downloader',
        url=PHISHING_FEED_URL,
        output_path=PHISHING_CURRENT_FILE_PATH,
        hash_variable_key=PHISHING_CURRENT_HASH_VARIABLE_KEY,
    )
    change_verifier = ChangeVerifierOperator(
        task_id='change_verifier',
        current_file=PHISHING_CURRENT_FILE_PATH,
        current_hash_variable_key=PHISHING_CURRENT_HASH_VARIABLE_KEY,
        previous_hash_variable_key=PHISHING_PREVIOUS_HASH_VARIABLE_KEY,
    )

    publisher = S3PublisherOperator(
        task_id="publisher",
        bucket_name="phishpipe-bucket",
        paths=[PHISHING_CURRENT_FILE_PATH],
        s3_prefix="phishing",
    )

    downloader >> change_verifier >> publisher
