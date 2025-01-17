import gzip
import base64
import json
import logging

class MessageProcessor:
    def __init__(self, data_ingestor):
        self.data_ingestor = data_ingestor

    def process_message(self, message_body):
        try:
            decoded_message = gzip.decompress(base64.b64decode(message_body)).decode('utf-8')
            data = json.loads(decoded_message)
            logging.info(f"Message processed: {data}")

            self.data_ingestor.process_and_insert_words(data["words"])
            logging.info("Data inserted successfully.")
        except Exception as e:
            logging.error(f"Error processing message: {e}")

