""" routes for /api/v1/speech """


from flask import Blueprint, request, Response, url_for
from ai_support_api.responses import single_envelope
from ai_support_api.speech import service
from ai_support_api.uploads import read_upload
from ai_support_api.speech.models import SpeechSynthesisRequest

speech_bp = Blueprint("speech", __name__)

UPLOAD_FILE = "file"

@speech_bp.post("/synthesis")
def synthesize():
    data = SpeechSynthesisRequest.model_validate(request.get_json(silent=True) or {})
    audio = service.synthesize_speech(data.text, data.voice_id, data.engine)

    # formatting our headers to tell the client how to handle the file data we're sending back
    return Response (
        audio, 
        mimetype="audio/mpeg",
        headers={"Content-Disposition": 'attachment; filename="polly-speech.mp3"'}
    )


@speech_bp.post("/transcriptions")
def start_transcriptions():

    audio, filename = read_upload(
        request.files.get(UPLOAD_FILE),
        allowed_extensions=service.ALLOWED_AUDIO_EXTENSIONS,
        max_bytes=service.MAX_AUDIO_BYTES
    )

    job = service.start_transcription_job(audio, filename)

    response = single_envelope(job)
    response.headers["Location"] = url_for("speech.get_transcription", job_name=job["job_name"])

    return response, 202        # returning 202 - ACCEPTED


@speech_bp.post("/transcriptions/<job_name>")
def get_transcription(job_name: str):   
    return single_envelope(service.get_transcription_job(job_name))