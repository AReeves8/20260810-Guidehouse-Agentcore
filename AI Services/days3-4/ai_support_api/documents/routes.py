""" routes for /api/v1/documents """


from flask import Blueprint, request
from ai_support_api.responses import single_envelope
from ai_support_api.documents import service
from ai_support_api.uploads import read_upload

documents_bp = Blueprint("documents", __name__)

# each route that needs to take in a file can reuse this property name
UPLOAD_FILE = "file"

@documents_bp.post("/analyze")
def analyze_attachements():

    attachment = read_upload(
        request.files.get(UPLOAD_FILE),
        allowed_extensions=service.ALLOWED_EXTENSIONS,
        max_bytes=service.MAX_IMAGE_BYTES
    )

    # passing in only the bytes
    return single_envelope(service.read_attachment(attachment[0]))
