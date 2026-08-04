from pydantic import BaseModel, Field


# --- STRICT JSON ENFORCEMENT (Pydantic) ---
# This forces the LLM to output predictable data, preventing application crashes.

class IncidentAnalysis(BaseModel):
    root_cause_summary: str = Field(description="A brief summary of the suspected root cause.")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0")
    recommended_action: str = Field(description="The immediate next step to resolve the incident.")


class AlertPayload(BaseModel):
    alert_text: str
