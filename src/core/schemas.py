from pydantic import BaseModel, Field


# --- STRICT JSON ENFORCEMENT (Pydantic) ---
# This forces the LLM to output predictable data, preventing application crashes.

class SearchIncidentsSchema(BaseModel):
    query: str = Field(
        ...,
        description="The semantic search query describing the current incident symptoms. Used to find similar historical outages."
    )


class LiveMetricsSchema(BaseModel):
    service_name: str = Field(
        ...,
        description="The name of the internal microservice to query (e.g., 'payment-gateway', 'auth-service')."
    )
