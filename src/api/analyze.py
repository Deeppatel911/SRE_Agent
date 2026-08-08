from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from src.core.schemas import AlertPayload, IncidentAnalysis
from src.services.llm import analyze_incident_with_llm

import asyncio
from src.api.celery_app import run_agent_task, celery_app

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


@router.websocket("/ws/diagnose")
async def websocket_diagnose(websocket: WebSocket):
    await websocket.accept()

    try:
        # 1. Listen for the raw PagerDuty alert
        alert = await websocket.receive_text()
        # await websocket.send_text("Status: Alert acknowledged. Spawning AI SRE Agent...")
        print(f"📥 [WEBSOCKET] Received alert: {alert}")

        # 2. Trigger the Celery task / Dispatch to the Celery background worker
        task = run_agent_task.delay(alert)
        # await websocket.send_text(f"Status: Agent deployed. Task ID -> {task.id}")
        await websocket.send_json({"task_id": task.id, "status": "STARTED"})

        # Asynchronously monitor the Celery task state
        # while not task.ready():
        #     await asyncio.sleep(0.5)
        #
        #     # Push the final synthesized Root Cause Analysis to the client
        # if task.successful():
        #     final_diagnosis = task.result
        #     await websocket.send_text(final_diagnosis)
        # else:
        #     await websocket.send_text(f"Error: Agent execution failed. Trace: {task.traceback}")

        # 3. Asynchronously monitor Redis with a 60-second timeout
        timeout_seconds = 60
        elapsed_time = 0

        while elapsed_time < timeout_seconds:
            task_result = celery_app.AsyncResult(task.id)

            if task_result.state == 'SUCCESS':
                # Push the final RCA payload to the client
                await websocket.send_json({
                    "status": "SUCCESS",
                    "result": task_result.result
                })
                break

            elif task_result.state == 'FAILURE':
                # Push error traces to the client
                await websocket.send_json({
                    "status": "FAILURE",
                    "error": str(task_result.info)
                })
                break

            # Non-blocking pause for 0.5s before checking Redis again
            await asyncio.sleep(0.5)
            elapsed_time += 0.5

        else:
            # This 'else' triggers if the while loop completes without hitting a 'break'
            await websocket.send_json({
                "status": "TIMEOUT",
                "error": "Agent execution exceeded 60 seconds. Aborting."
            })

    except WebSocketDisconnect:
        print("Client disconnected from WebSocket.")
