# app/tasks.py

import pika
import json
import uuid

def publish_task(data):
    # Connect to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    # Ensure the queue exists and is durable
    channel.queue_declare(queue="task_queue", durable=True)

    # Assign a unique task ID
    task_id = str(uuid.uuid4())
    data["task_id"] = task_id

    # Publish the task to the queue
    channel.basic_publish(
        exchange="",
        routing_key="task_queue",
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
    )

    # Close the connection
    connection.close()

    return task_id
