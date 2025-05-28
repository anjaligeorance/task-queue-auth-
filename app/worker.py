# app/worker.py

import json
import pika
from app.db import insert_task  # Function that inserts into MongoDB
from app.cache import redis_client  # Redis client for task status caching

def callback(ch, method, properties, body):
    # Deserialize the message
    task_data = json.loads(body)
    task_id = task_data["task_id"]

    # Update status in Redis
    redis_client.set(task_id, "processing")

    # Simulate task processing (insert into DB)
    insert_task(task_data)

    # Update status in Redis again
    redis_client.set(task_id, "completed")

    # Acknowledge message
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    # Ensure the queue exists
    channel.queue_declare(queue="task_queue", durable=True)

    # Handle one message at a time
    channel.basic_qos(prefetch_count=1)

    # Set callback to consume messages
    channel.basic_consume(queue="task_queue", on_message_callback=callback)

    print("Worker started. Waiting for tasks...")

    # Start consuming messages
    channel.start_consuming()

# Only run if this file is executed directly
if __name__ == "__main__":
    start_worker()
