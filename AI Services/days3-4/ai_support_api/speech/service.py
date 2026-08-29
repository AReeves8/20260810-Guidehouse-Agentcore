""" 
    performing text-to-speech and speech-to-text operations

    Polly - text-to-speech
    Transcribe - speech-to-text
 """


import json
import uuid

from ai_support_api.config import BUCKET_NAME
from ai_support_api.aws import get_client

# file extensions allowed by Transcribe
ALLOWED_AUDIO_EXTENSIONS = {"mp3", "mp4", "m4a", "wav", "flac", "ogg", "webm"}

# file size limit for this demo - 20 MB
#       Transcribe can do 4 hours or 2 GB of data through the API
MAX_AUDIO_BYTES = 20 * 1024 * 1024


def synthesize_speech(text: str, voice_id: str, engine: str) -> bytes:
    """ using Polly to turn text into audio (.mp3 specified) """

    response = get_client("polly").synthesize_speech(
        Text=text, 
        VoiceId=voice_id,
        Engine=engine,
        OutputFormat="mp3"
    )

    # reading the file given from aws and returning the bytes
    return response["AudioStream"].read()


def start_transcription_job(audio_bytes: bytes, filename: str) -> dict:
    """ store the given audio in s3 and then tell transcribe to look for it to start the transcription job """

    # parse off the file extension to use later
    extension = filename.rsplit(".", 1)[-1].lower()

    # generate a unique job name for this file
    job_name = f"support-api-{uuid.uuid4().hex}"

    # putting the job name and extension together to create the new unique file name
    audio_key = f"audio/{job_name}.{extension}"

    # storing the given audio into s3 with the unique file name
    get_client("s3").put_object(Bucket=BUCKET_NAME, Key=audio_key, Body=audio_bytes)

    get_client("transcribe").start_transcription_job(
        TranscriptionJobName=job_name,
        LanguageCode="en-US",
        MediaFormat=extension,
        Media={"MediaFileUri": f"s3://{BUCKET_NAME}/{audio_key}"},
        OutputBucketName=BUCKET_NAME,
        OutputKey=f"transcripts/{job_name}.json"
    )

    return {"job_name": job_name, "status": "IN_PROGRESS"}


def get_transcription_job(job_name: str) -> dict:
    """ get an existing job out of AWS Transcribe """

    # retrieving the job status from Transcribe
    job = get_client("transcribe").get_transcription_job(
        TranscriptionJobName=job_name
    )["TranscriptionJob"]

    # grabbing status of the transcription job to see if it is finished
    status = job["TranscriptionJobStatus"]

    result = {"job_name": job_name, "status": status}

    if status == "COMPLETED":

        # retrieving the transcript out of S3
        response = get_client("s3").get_object(
            Bucket=BUCKET_NAME, 
            Key=f"transcripts/{job_name}.json"
        )
        payload = json.loads(response["Body"].read())

        # adding it to the results
        result["transcript"] = payload["results"]["transcripts"][0]["transcript"]

    elif status == "FAILED":

        # including the reason the transcription failed
        result["failure_reason"] = job.get("FailureReason", "unknown")

    return result