from typing import Literal
from pydantic import BaseModel, Field, field_validator

# different severity levels for the model to categorize alerts into
Severity = Literal["SEV1", "SEV2", "SEV3"]

# first line of the class needs to be a docstring with model instructions
class Triage(BaseModel):
    """ A first-pass severity assessment of a single production alert.

        Judge only from the alert text provided. Do not assume facts it does not state. 
        Do not propse a remediation -- this is an assessment that a human will read before deciding to act.
    """

    severity: Severity = Field(
        description=(
            "SEV1 = complete outage or data loss. "
            "SEV2 = major degedation, many users affected. "
            "SEV3 = minor or internal-only impact. "
        )
    )

    service: str = Field(
        description="The name of the affected service. Copy verbatim from alert text."
    )

    customer_facing : bool = Field(
        description="True if an end-user outside the company would notice the issue."
    )

    summary: str = Field(
        description="One sentence summary of the alert. Written in plain english. No jargon or acronyms."
    )

    suspected_cause: str | None = Field(
        default=None, 
        description=(
            "A likely cause of the issue if the alert text points at one. Do not provide a cause if one is not evident. "
            "Examples include a deployment id, a configuration change, or an unhealthy service. "
            "Omit entirely if there is no suspected cause of the issue."
        )
    )

class StatusUpdate(BaseModel):
    """A short public status-page post, drafted from the same alert."""

    headline: str = Field(
        description="Under 10 words. What a customer would recognise as their problem."
    )
    body: str = Field(
        description=(
            "Two sentences maximum. What is affected and that we are investigating. "
            "No root cause, no blame, no internal service names, no ETA."
        )
    )

class IncidentBrief(BaseModel):
    """ the merged result of the triage and drafting chains """

    alert: str
    triage: Triage
    status_update: StatusUpdate

    @property
    def needs_page(self) -> bool:
        """ should the alert wake someone up in the middle of the night? """

        # only need to page a human for severe issues that would affect customers
        return self.triage.severity in ("SEV1", "SEV2") and self.triage.customer_facing

class Diagnosis(BaseModel):
    """A runbook-grounded assessment of an alert.

    Answer ONLY from the runbook excerpts provided to you. The excerpts are the
    company's own operational policy; your own general knowledge about how
    software systems usually behave is NOT a source and must not be used to
    fill a gap.

    If the excerpts do not cover the situation, say so by setting
    `grounded` to false rather than producing a plausible answer.
    """

    grounded: bool = Field(
        description=(
            "True only if the runbook excerpts directly support your answer. "
            "False if you had to rely on general knowledge or guesswork."
        )
    )

    severity: Severity | None = Field(
        default=None,
        description=(
            "The severity the runbooks assign to this situation. Null if the "
            "excerpts do not establish one."
        )
    )

    recommended_action: str = Field(
        description=(
            "The next concrete step, as the runbooks describe it. If the "
            "excerpts do not cover this situation, say exactly what is missing "
            "instead of guessing."
        )
    )

    sources: list[str] = Field(
        description=(
            "The exact runbook filenames you used, copied from the 'source:' line of each excerpt. "
            "If you do not use or have any sources, populate with an empty list. Ex: []"
        )
    )

    requires_approval: bool = Field(
        default=False,
        description=(
            "True if the runbooks say the recommended action needs a second "
            "person's sign-off before it may be carried out."
        ),
    )