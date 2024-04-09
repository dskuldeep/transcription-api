import whisper
import boto3
import os

model = whisper.load_model("base")

def transcribe(filepath):
    print("Entered the transcription phase")
    print(filepath)

    bucket_name = 'zetachi'
    object_key = filepath
    filename = os.path.basename(object_key)
    local_filepath  = os.path.join(os.getcwd(), filename)

    s3 = boto3.client('s3')

    s3.download_file(bucket_name, object_key, local_filepath)

    transcripted_text = model.transcribe(local_filepath)
    return transcripted_text
