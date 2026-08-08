from celery import Celery
from src.agent.orchestrator import run_sre_agent
import httpx

# Initialize Celery with Redis as both the message broker and backend state store
celery_app = Celery(
    "sre_agent_tasks",
    broker="redis://host.docker.internal:6379/0",
    backend="redis://host.docker.internal:6379/1"
) # use localhost when running the server on your host machine

# Optional: Ensure Celery strictly serializes complex data to JSON
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True
)


@celery_app.task(name="run_agent_task", acks_late=True)
def run_agent_task(incident_alert: str, callback_url: str = None):
    """
    Wraps the AI execution loop in a background task.
    """
    # return run_sre_agent(incident_alert)

    # 1. Run the AI Agent
    final_diagnosis = run_sre_agent(incident_alert)

    # 2. If a callback URL was provided (Webhook route), POST the results
    if callback_url:
        try:
            # Send the result back to n8n
            response = httpx.post(callback_url, json={"result": final_diagnosis}, timeout=10.0)
            print(f"✅ [WEBHOOK] Successfully posted RCA to {callback_url} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ [WEBHOOK] Failed to post to callback URL: {e}")

    # Return for the Redis backend (used by WebSockets)
    return final_diagnosis
