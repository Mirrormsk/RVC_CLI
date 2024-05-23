import pika
import os

from config import settings

rmq_parameters = pika.URLParameters(settings.rmq_connection_url)
connection = pika.BlockingConnection(rmq_parameters)


channel = connection.channel()
