from datetime import datetime
from airflow import DAG
from operators.phishing_getter import PhishingGetterOperator
from operators.change_verifier import ChangeVerifier
from config import PHISHING_FEED_URL, CURRENT_FILE, PREVIOUS_FILE

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
        output_path=CURRENT_FILE
    )
    change_verifier = ChangeVerifier(
        task_id='change_verifier',
        current_file=CURRENT_FILE,
        previous_file=PREVIOUS_FILE
    )

    downloader >> change_verifier
