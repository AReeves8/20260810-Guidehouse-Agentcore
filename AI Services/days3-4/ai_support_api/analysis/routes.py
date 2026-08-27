""" routes for /api/v1/analysis """

from flask import Blueprint, request
from ai_support_api.responses import single_envelope
from ai_support_api.analysis import service
from ai_support_api.analysis.models import TextAnalysisRequest, TicketTriageRequest


analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.post("/sentiment")
def sentiment_analysis():
    data = TextAnalysisRequest.model_validate(request.get_json(silent=True) or {})
    return single_envelope(service.analyze_sentiment(data.text))


@analysis_bp.post("/priority-triage")
def priority_triage():
    data = TicketTriageRequest.model_validate(request.get_json(silent=True) or {}) 
    return single_envelope(service.triage_priority(data.ticket_id, data.body))
