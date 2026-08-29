from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class SpeechSynthesisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Polly has a limit of only 3000 characters compared to Comprehend's 5000
    text: str = Field(min_length=1, max_length=3000)
    voice_id: str = Field(default="Joanna", min_length=1, max_length=64)

    # since there are only a few options for engine, define those here
    engine: Literal["standard", "neural", "long-form", "generative"] = "standard"
