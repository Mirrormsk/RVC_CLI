import json
import os
from dotenv import load_dotenv
from rmq_config import channel
from rvc_service import rvc_service
import logging


load_dotenv(dotenv_path='.env')

logger = logging.getLogger(__name__)


def callback(ch, method, properties, body):
    json_data = json.loads(body)
    logger.info('Received %r', json_data)

    try:
        rvc_service.retrieve_command(command_data=json_data)
    except Exception as e:
        logging.error(e, exc_info=True)


queue_name = os.getenv('QUEUE_NAME')


channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)

if __name__ == '__main__':

    logger.info('Waiting for messages')
    channel.start_consuming()
