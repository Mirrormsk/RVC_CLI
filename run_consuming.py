import json
import os

import pika
from dotenv import load_dotenv
from pika.exceptions import AMQPConnectionError

# from rmq_config import create_channel
from control_api.rvc_service import rvc_service
import logging
from config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_channel():
    parameters = pika.URLParameters(settings.rmq_connection_url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=settings.queue_name)
    return connection, channel


def callback(ch, method, properties, body):
    json_data = json.loads(body)
    logger.info('Received %r', json_data)
    try:
        rvc_service.retrieve_command(command_data=json_data)
    except Exception as e:
        logger.error(e, exc_info=True)


def main():
    while True:
        try:
            connection, channel = create_channel()
            channel.basic_consume(queue=settings.queue_name, on_message_callback=callback, auto_ack=True)
            logger.info('Waiting for messages')
            channel.start_consuming()
        except AMQPConnectionError as e:
            logger.error(f'Connection error: {e}')
            continue
        except KeyboardInterrupt:
            channel.stop_consuming()
            connection.close()
            break


if __name__ == '__main__':
    main()
