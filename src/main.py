from fastapi import FastAPI
from src.api.analyze import router as analyze_router

app = FastAPI(
    title="Automated SRE Incident Responder",
    description="Microservice for autonomous alert analysis and root-cause estimation.",
    version="1.0.0"
)

# Register API routes
app.include_router(analyze_router, prefix="/api/v1")
