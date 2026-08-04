from fastapi import APIRouter, HTTPException
from src.core.schemas import AlertPayload, IncidentAnalysis
from src.services.llm import analyze_incident_with_llm

router = APIRouter()

# --- THE API ENDPOINT ---
@router.post("/analyze")
async def trigger_analysis(payload: AlertPayload):
    try:
        analysis_dict = analyze_incident_with_llm(payload.alert_text)
        validated_data = IncidentAnalysis(**analysis_dict)
        return {"status": "success", "data": validated_data.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
