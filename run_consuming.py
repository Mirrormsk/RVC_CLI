import json
import os

import pika
from dotenv import load_dotenv
from rmq_config import create_channel
from rvc_service import rvc_service
import logging
from config import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def callback(ch, method, properties, body):
    json_data = json.loads(body)
    logger.info('Received %r', json_data)
    try:
        rvc_service.retrieve_command(command_data=json_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error(e, exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag)


def main():
    connection, channel = create_channel()

    channel.basic_consume(queue=settings.queue_name, on_message_callback=callback, auto_ack=True)

    try:
        logger.info('Waiting for messages')
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    except pika.exceptions.StreamLostError as e:
        logger.error(f'StreamLostError: {e}, retrying...')
        main()
    finally:
        connection.close()


if __name__ == '__main__':
    main()

