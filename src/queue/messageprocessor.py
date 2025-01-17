import gzip
import base64
import json
import logging

class MessageProcessor:
    def __init__(self, data_ingestor):
        self.data_ingestor = data_ingestor

    def process_message(self, message_body):
        try:
            # Decodifica y descomprime el mensaje
            decoded_message = gzip.decompress(base64.b64decode(message_body)).decode('utf-8')
            data = json.loads(decoded_message)
            logging.info(f"Message processed: {data}")

            # Construye el diccionario en el formato esperado
            book_data = {
                "book": data.get("book", "Unknown Book"),
                "author": data.get("author", "Unknown Author"),
                "words": data.get("words", [])
            }

            # Llama al método del ingestor con el formato correcto
            self.data_ingestor.process_and_insert_words(book_data)
            logging.info("Data inserted successfully.")
        except Exception as e:
            logging.error(f"Error processing message: {e}")


