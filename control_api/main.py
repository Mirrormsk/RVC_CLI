from control_api.rmq_config import channel


def callback(ch, method, properties, body):

    print(f"Received: '{body}'")



queue_name = 'training'

channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True  # Автоматическое подтверждение обработки сообщений
)

print('Waiting for messages. To exit, press Ctrl+C')
channel.start_consuming()
