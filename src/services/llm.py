import json
from groq import Groq
from langfuse import observe

from src.core.config import settings
from src.core.schemas import IncidentAnalysis
from src.prompts.sre_prompts import SRE_SYSTEM_PROMPT, SRE_USER_PROMPT

# Initialize Groq client using central config
client = Groq(api_key=settings.GROQ_API_KEY)


# --- THE OBSERVABILITY TRACE (Langfuse) ---
# The @observe decorator automatically logs latency, inputs, and outputs to Langfuse.
@observe()
def analyze_incident_with_llm(alert: str) -> dict:
    """Invokes Groq LLM with forced JSON mode and Langfuse telemetry."""

    formatted_system_prompt = (
        f"{SRE_SYSTEM_PROMPT}\n\n"
        f"Required JSON Schema:\n{IncidentAnalysis.model_json_schema()}"
    )

    formatted_user_prompt = SRE_USER_PROMPT.format(alert_text=alert)

    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": formatted_user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=settings.MODEL_TEMPERATURE
    )

    raw_json = response.choices[0].message.content
    return json.loads(raw_json)
