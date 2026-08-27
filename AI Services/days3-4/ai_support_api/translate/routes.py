""" routes for /api/v1/translation """


from flask import Blueprint, request
from ai_support_api.responses import single_envelope
from ai_support_api.translate import service
from ai_support_api.translate.models import TranslationRequest

translation_bp = Blueprint("translation", __name__)

@translation_bp.post("")
def translate_route():

    # validating request body
    data = TranslationRequest.model_validate(request.get_json(silent=True) or {})

    # returning the formatted response from AWS
    return single_envelope(service.translate(data.text, data.source_language, data.target_language))