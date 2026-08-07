import random
from qdrant_client import QdrantClient
from langfuse import observe
import warnings

# ---------------------------------------------------------
# Mute Qdrant Warnings
# ---------------------------------------------------------
warnings.filterwarnings("ignore", category=UserWarning, module="qdrant_client")

# ---------------------------------------------------------
# Security: Principle of Least Privilege
# We instantiate the client here and ONLY expose the query method
# to the agent. It has zero ability to call .add() or .delete()
# ---------------------------------------------------------
qdrant_client = QdrantClient(url="http://localhost:6333",check_compatibility=False)
qdrant_client.set_model("BAAI/bge-small-en-v1.5")


@observe(as_type="tool") # Automatically logs inputs, outputs, and latency
def search_past_incidents(query: str) -> str:
    """
    Searches the local Qdrant database for similar past SRE incidents.
    Returns structured text containing the root causes and resolutions.
    """
    print(f"🔧 Tool Execution: Searching past incidents for -> '{query}'")

    search_results = qdrant_client.query(
        collection_name="sre_incidents",
        query_text=query,
        limit=3,  # Returning top 3 matches to balance context vs token limit
        score_threshold=0.65  # Adjust based on embedding model sensitivity
    )

    if not search_results:
        print("⚠️ No results exceeded score_threshold=0.65")
        return "No relevant past incidents found in the knowledge base."

    # Format the payload cleanly for the LLM to read
    formatted_context = []
    for result in search_results:
        meta = result.metadata

        score = result.score
        print(f"  └─ Found Match: '{meta.get('title')}' (Score: {score:.3f})")

        formatted_context.append(
            f"Title: {meta.get('title')}\n"
            f"Root Cause: {meta.get('root_cause')}\n"
            f"Resolution: {meta.get('resolution')}\n"
            f"Similarity Score: {score:.3f}"
        )

    return "\n\n---\n\n".join(formatted_context)


@observe(as_type="tool") # Automatically logs inputs, outputs, and latency
def get_live_metrics(service_name: str) -> str:
    """
    Mocks a live observability platform (like Datadog/Prometheus).
    Returns real-time CPU, Memory, and Error Rate metrics.
    """
    print(f"🔧 Tool Execution: Fetching live metrics for -> '{service_name}'")

    # We will hardcode a failing service here to test the agent's diagnostic skills later
    if service_name.lower() == "payment-gateway":
        cpu = "98%"
        memory = "85%"
        error_rate = "12.4%"
        status = "CRITICAL 🚨"
    else:
        # Generate healthy baseline metrics for any other service queried
        cpu = f"{random.randint(10, 40)}%"
        memory = f"{random.randint(20, 50)}%"
        error_rate = f"{random.uniform(0.1, 1.5):.2f}%"
        status = "HEALTHY ✅"

    return (
        f"Metrics for {service_name}:\n"
        f"Status: {status}\n"
        f"CPU Usage: {cpu}\n"
        f"Memory Usage: {memory}\n"
        f"Error Rate: {error_rate}"
    )
