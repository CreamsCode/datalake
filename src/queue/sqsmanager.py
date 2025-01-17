import boto3
import logging

class SQSManager:
    def __init__(self, queue_url, region_name="us-east-1"):
        self.queue_url = queue_url
        self.client = boto3.client("sqs", region_name=region_name)

    def receive_messages(self, max_messages=1, wait_time=10):
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time
        )
        return response.get("Messages", [])

    def delete_message(self, receipt_handle):
        self.client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )
        logging.info("Message deleted from SQS.")
