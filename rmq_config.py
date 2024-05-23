import pika
import os

from config import settings


def create_channel() -> tuple[pika.BlockingConnection, pika.adapters.blocking_connection.BlockingChannel]:
    rmq_parameters = pika.URLParameters(settings.rmq_connection_url)
    connection = pika.BlockingConnection(rmq_parameters)
    channel = connection.channel()
    return connection, channel
