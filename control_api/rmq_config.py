import pika
import os

connection_params = pika.ConnectionParameters(
    host=os.getenv("RABBITMQ_HOST", 'localhost'),
    port=os.getenv("RABBITMQ_PORT", 5672),
    virtual_host='/',
    credentials=pika.PlainCredentials(
        username=os.getenv("RABBITMQ_USER", 'guest'),  # Имя пользователя по умолчанию
        password=os.getenv("RABBITMQ_PASS", 'guest')   # Пароль по умолчанию
    )
)

connection = pika.BlockingConnection(connection_params)

channel = connection.channel()
