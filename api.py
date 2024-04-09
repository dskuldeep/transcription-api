from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from typing import List
import boto3
import uuid
from mq import transcription_consumer
import json
import uvicorn
import threading
from io import BytesIO
import logging
import pika
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

logging.basicConfig(level=logging.INFO)

RABBITMQ_HOST = 'api.getzetachi.com'
RABBITMQ_PORT = 5672
RABBITMQ_USERNAME = 'Kuldeep'
RABBITMQ_PASSWORD = "Kuldeep@1997"
RABBITMQ_QUEUE_NAME = 'transcription_que'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=pika.PlainCredentials(username=RABBITMQ_USERNAME, password=RABBITMQ_PASSWORD)))
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE_NAME, durable=True)

s3 = boto3.client('s3', aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                  region_name='us-east-1')

@app.post("/upload/")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    allowed_extensions = {'mp3', 'wav', 'flac', 'm4a'}
    file_extension = file.filename.split('.')[-1]
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported File Format")
    
    file_path  = f"{uuid.uuid4()}.{file_extension}"
    file_contents = await file.read()
    background_tasks.add_task(upload_to_s3, file_contents, "zetachi", file_path)

    #Pub to rabbit mq
    try:
        message = {"file_path": file_path}
        print("Message published to MQ")
        channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE_NAME, body=json.dumps(message))
    except Exception as e:
        logging.error(f"Error publishing to RabbitMQ: {e}")
        # Handle the error appropriately, e.g., retry, log, or raise

    return {"detail": "File uploaded successfully"}


def upload_to_s3(file_contents, bucket_name: str, file_path: str):
    file = BytesIO(file_contents)
    s3.upload_fileobj(file, bucket_name, file_path)

def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8888)

def start_consumer():
    transcription_consumer()

if __name__ == "__main__":
    # Create threads for running the server and the consumer concurrently
    server_thread = threading.Thread(target=start_server)
    consumer_thread = threading.Thread(target=start_consumer)

    # Start both threads
    server_thread.start()
    consumer_thread.start()

    # Wait for both threads to finish
    server_thread.join()
    consumer_thread.join()
