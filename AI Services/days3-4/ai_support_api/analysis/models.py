from pydantic import BaseModel, ConfigDict, Field

class TextAnalysisRequest(BaseModel):

    model_config = ConfigDict(extra="forbid")

    # AWS Comprehend has a 5000 character limit
    text: str = Field(min_length=1, max_length=5000)

class TicketTriageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_id: int = Field(ge=1)
    
    # AWS Comprehend has a 5000 character limit
    body: str = Field(min_length=1, max_length=5000)