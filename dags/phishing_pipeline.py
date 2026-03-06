from datetime import timedelta, datetime
from airflow import DAG
from operators.phishing_getter import PhishingGetterOperator
from operators.change_verifier import ChangeVerifierOperator
from operators.s3_publisher import S3PublisherOperator
from operators.kafka_notifier import KafkaNotifierOperator
from config import (
    PHISHING_FEED_URL,
    PHISHING_CURRENT_FILE_PATH,
    PHISHING_CURRENT_HASH_VARIABLE_KEY,
    PHISHING_PREVIOUS_HASH_VARIABLE_KEY,
)

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False,
}

with DAG(
        dag_id='phishing_pipeline',
        default_args=default_args,
        description='Download phishing feed, detect changes, and publish to S3',
        schedule_interval='@daily',
        start_date=datetime(2026, 2, 2),
        catchup=False,
        tags=['phishing', 'pipeline', 'data-ingestion'],
        max_active_runs=1,
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
        task_id='publisher',
        bucket_name='phishpipe-bucket',
        paths=[PHISHING_CURRENT_FILE_PATH],
        s3_prefix='phishing',
    )

    kafka_notifier = KafkaNotifierOperator(
        task_id='kafka_notifier',
        topic='phishing_updates',
        bootstrap_servers='kafka:9092',
        message={
            "event": "new_phishing_data",
            "file": PHISHING_CURRENT_FILE_PATH,
            "timestamp": str(datetime.utcnow())
        },
    )

    downloader >> change_verifier >> publisher >> kafka_notifier