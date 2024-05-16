import json
import os

import pika
from dotenv import load_dotenv
from pika.exceptions import AMQPConnectionError

# from rmq_config import create_channel
from rvc_service import rvc_service
import logging
from config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_channel():
    parameters = pika.URLParameters(settings.rabbitmq_url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=settings.queue_name, durable=True)
    return connection, channel


def callback(ch, method, properties, body):
    json_data = json.loads(body)
    logger.info('Received %r', json_data)
    try:
        rvc_service.retrieve_command(command_data=json_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(e, exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag)


def main():
    while True:
        try:
            connection, channel = create_channel()
            channel.basic_consume(queue=settings.queue_name, on_message_callback=callback, auto_ack=False)
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
