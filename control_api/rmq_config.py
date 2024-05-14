import pika
import os

from dotenv import load_dotenv

load_dotenv()

RMQ_CONNECTION_URL = os.getenv("RMQ_CONNECTION_URL")


rmq_parameters = pika.URLParameters(RMQ_CONNECTION_URL)
connection = pika.BlockingConnection(rmq_parameters)


channel = connection.channel()
