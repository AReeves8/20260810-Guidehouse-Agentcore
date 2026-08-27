from pydantic import BaseModel, ConfigDict, Field

class TranslationRequest(BaseModel):

    # not allowing any other properties
    model_config = ConfigDict(extra="forbid")


    text: str = Field(min_length=1, max_length=5000)

    # "auto" lets aws decide what language to use if one isn't provided
    source_language: str = Field(default="auto", min_length=2, max_length=5)

    target_language: str = Field(min_length=2, max_length=5)
