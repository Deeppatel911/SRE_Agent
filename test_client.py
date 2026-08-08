import asyncio
import json
import websockets


async def test_websocket():
    # Notice the route aligns with your router prefix: /api/v1/ws/diagnose
    uri = "ws://localhost:8000/api/v1/ws/diagnose"
    test_alert = "PagerDuty Alert: The payment-gateway service is dropping connections and throwing 500 errors. Customers cannot check out."

    print(f"🔌 Connecting to WebSocket at {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print(f"📤 Sending alert: {test_alert}\n")
            await websocket.send(test_alert)

            while True:
                response_str = await websocket.recv()
                data = json.loads(response_str)
                status = data.get("status")

                if status == "STARTED":
                    print(f"🚀 Task Dispatched to Celery! Task ID -> {data.get('task_id')}")
                    print("⏳ Waiting for background SRE Agent diagnosis...\n")

                elif status == "SUCCESS":
                    print("=" * 60)
                    print("🎉 FINAL SRE DIAGNOSIS RECEIVED VIA WEBSOCKET:")
                    print("=" * 60)
                    print(data.get("result"))
                    print("=" * 60)
                    break

                elif status in ["FAILURE", "TIMEOUT"]:
                    print(f"❌ Execution failed with status [{status}]: {data.get('error')}")
                    break

    except Exception as e:
        print(f"⚠️ Connection error: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
