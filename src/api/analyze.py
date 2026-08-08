from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

import asyncio
from src.api.celery_app import run_agent_task, celery_app

from src.core.schemas import WebhookPayload

router = APIRouter()

# --- THE API ENDPOINT ---


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


@router.post("/webhook/diagnose")
async def webhook_diagnose(payload: WebhookPayload):
    print(f"📥 [WEBHOOK] Received alert via n8n. Callback URL: {payload.callback_url}")

    # Trigger the Celery task, passing both the alert AND the callback URL
    task = run_agent_task.delay(payload.alert_text, payload.callback_url)

    # Immediately return a 200 OK to n8n so it doesn't hang
    return {
        "status": "STARTED",
        "task_id": task.id,
        "message": "Agent dispatched. Results will be posted to the callback URL."
    }
