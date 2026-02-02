from datetime import datetime
from airflow import DAG
from operators.phishing_getter import PhishingGetterOperator 

URL = 'http://svn.code.sf.net/p/aper/code/phishing_reply_addresses'
OUTPUT_PATH = '/opt/airflow/data/phishing_feed.csv'

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 2, 2),
}

with DAG(
    dag_id='phishing_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    downloader = PhishingGetterOperator(
        task_id='downloader',
        url=URL,
        output_path=OUTPUT_PATH
    )
