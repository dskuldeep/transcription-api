import pika
import json
from transcribe import transcribe
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import logging

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@api.getzetachi.com/db1"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base = declarative_base()

class Transcription(Base):
    __tablename__ = "transcriptions"

    id  = Column(Integer, primary_key=True, index=True)
    audio_file_path  = Column(String)
    transcript_text = Column(String)
    status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

RABBITMQ_HOST = 'api.getzetachi.com'
RABBITMQ_PORT = 5672
RABBITMQ_USERNAME = 'Kuldeep'
RABBITMQ_PASSWORD = "Kuldeep@1997"
RABBITMQ_QUEUE_NAME = 'transcription_que'
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=pika.PlainCredentials(username=RABBITMQ_USERNAME, password=RABBITMQ_PASSWORD)))
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE_NAME, durable=True)

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def save_transcription_to_db(audio_file_path: str, transcription_text: str):
    try:
        session = SessionLocal()
        transcription = Transcription(audio_file_path=audio_file_path, transcript_text=transcription_text)
        session.add(transcription)
        session.commit()
        logging.info(f"Transcription saved to database. ID: {transcription.id}")
    except Exception as e:
        logging.error(f"Error occurred while saving transcription to database: {e}")
        session.rollback()
    finally:
        session.close()
        return transcription.id if transcription else None


def transcription_consumer():
    def callback(ch, method, properties, body):
        message = json.loads(body)
        file_path = message["file_path"]

        #Transcribe
        transcribe_text = transcribe(file_path)
        if transcribe_text:
            transcribe_text_json = json.dumps(transcribe_text)
            transcription_id = save_transcription_to_db(file_path, transcribe_text_json)
            if transcription_id:
                logging.info(f"Transcription saved with ID: {transcription_id}")
            else:
                logging.error("Failed to save transcription to database.")
        else:
            logging.error("Transcription text is empty.")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=RABBITMQ_QUEUE_NAME, on_message_callback=callback)
    channel.start_consuming()
