from typing import Any, Dict
from airflow.models import BaseOperator
from confluent_kafka import Producer
import json


class KafkaNotifierOperator(BaseOperator):
    def __init__(
            self,
            topic: str,
            bootstrap_servers: str,
            message: Dict[str, Any],
            **kwargs: Any
    ):

        """
        Custom Airflow operator to send messages to a Kafka topic.

        This operator is used to notify downstream systems that
        new data is available, e.g., after a successful S3 upload.

        Attributes:
            topic (str): Kafka topic name to which the message will be sent.
            bootstrap_servers (str): Kafka bootstrap servers, e.g., 'kafka:9092'.
            message (Dict[str, Any]): The payload to send. Will be JSON-serialized.
        """
    super().__init__(**kwargs)
    self.topic = topic
    self.bootstrap_servers = bootstrap_servers
    self.message = message


def execute(self, context: dict):
    """
    Execute the operator: send the message to Kafka.

    Steps:
        1. Connects to Kafka using the specified bootstrap servers.
        2. Produces the message to the specified topic.
        3. Registers a delivery callback to log success/failure.
        4. Flushes the producer to ensure all messages are delivered.

    Args:
        context (Dict[str, Any]): Airflow execution context (provided automatically).

    Raises:
        Exception: If Kafka delivery fails, the task will fail in Airflow.
    """
    self.log.info(f"Connecting to Kafka at {self.bootstrap_servers}...")

    # initialize producer
    producer = Producer({"bootstrap.servers": self.bootstrap_servers})

    def delivery_report(err, msg):
        if err is not None:
            self.log.error(f"Message delivery failed: {err}")
            # to ensure Airflow knows the task actually failed
            raise Exception(f"Kafka Error: {err}")
        else:
            self.log.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    self.log.info(f"Producing message to {self.topic}...")
    producer.produce(
        self.topic,
        json.dumps(self.message).encode("utf-8"),
        callback=delivery_report
    )

    # triggers the network call and callback
    producer.flush()
    self.log.info("Kafka flush complete.")
