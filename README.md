# Transcription API
## With Rabbit MQ Que and Database for Transcription

This service is designed to take in an audio file and generate the text of the language spoken in the audio file, uses the OpenAI Whisper Model and uses RabbitMQ for maintaining a que of pending trasncriptions. The service also uses a Postgresql Database to store the trasncribed audio and can be used by the client to fetch the transcription.

The audio files are stored in an Amazon S3 Bucket and the database maintains a record of the audio file used for each transcription.
