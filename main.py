import logging
import argparse
from src.queue.sqsmanager import SQSManager
from src.queue.messageprocessor import MessageProcessor
from src.mongo.connection import MongoDBConnectionManager
from src.mongo.ingestor import DataIngestor

def main(queue_url, region_name, ip, db_name):
    # Configuración de logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    logging.info("Iniciando el listener de SQS...")

    # Inicializar la conexión a MongoDB
    mongo_manager = MongoDBConnectionManager(ip=ip, db_name=db_name)
    mongo_manager.connect()
    data_ingestor = DataIngestor(mongo_manager)

    # Inicializar SQS Manager y Message Processor
    sqs_manager = SQSManager(queue_url=queue_url, region_name=region_name)
    message_processor = MessageProcessor(data_ingestor)

    logging.info("Escuchando mensajes en la cola SQS...")

    while True:
        try:
            # Recibir mensajes de SQS
            messages = sqs_manager.receive_messages()

            if not messages:
                logging.info("No se recibieron mensajes. Esperando...")
                continue

            for message in messages:
                # Procesar cada mensaje
                logging.info(f"Procesando mensaje: {message['MessageId']}")
                message_processor.process_message(message["Body"])

                # Eliminar el mensaje de SQS
                sqs_manager.delete_message(message["ReceiptHandle"])

        except Exception as e:
            logging.error(f"Error durante la ejecución: {e}")
        finally:
            mongo_manager.close()

if __name__ == "__main__":
    # Argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Listener de SQS para MongoDB")
    parser.add_argument("--queue_url", required=True, help="URL de la cola SQS")
    parser.add_argument("--region_name", default="us-east-1", help="Región de AWS")
    parser.add_argument("--ip", default="localhost", help="IP de MongoDB")
    parser.add_argument("--db_name", default="word_analysis", help="Nombre de la base de datos MongoDB")
    args = parser.parse_args()

    # Ejecutar el listener
    main(
        queue_url=args.queue_url,
        region_name=args.region_name,
        ip=args.mongo_uri,
        db_name=args.db_name
    )
