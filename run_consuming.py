import json
import os

import pika
from dotenv import load_dotenv
from rmq_config import create_channel
from rvc_service import rvc_service
import logging
from config import settings


logger = logging.getLogger(__name__)


def send_acknowledgment(properties):
    connection = pika.BlockingConnection(pika.URLParameters(settings.rmq_connection_url))
    ack_channel = connection.channel()
    ack_queue_name = properties.reply_to

    ack_message = {
        'status': 'accepted',
        'correlation_id': properties.correlation_id,
    }

    ack_channel.basic_publish(
        exchange='',
        routing_key=ack_queue_name,
        body=json.dumps(ack_message),
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
        ))
    connection.close()


def callback(ch, method, properties, body):
    json_data = json.loads(body)
    logger.info('Received %r', json_data)

    try:
        send_acknowledgment(properties)

        rvc_service.retrieve_command(command_data=json_data)

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error(e, exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag)


def main():
    connection, channel = create_channel()

    channel.basic_consume(queue=settings.queue_name, on_message_callback=callback, auto_ack=False)

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

