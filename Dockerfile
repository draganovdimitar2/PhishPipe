FROM puckel/docker-airflow:1.10.9

USER root
RUN pip install boto3
USER airflow
