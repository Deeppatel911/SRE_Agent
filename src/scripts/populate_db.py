import json
import os
from qdrant_client import QdrantClient

# Connect to the local Docker container
client = QdrantClient(url="http://localhost:6333")

# We use FastEmbed's default, highly-efficient local embedding model
client.set_model("BAAI/bge-small-en-v1.5")

collection_name = "sre_incidents"
data_path = os.path.join("data", "post_mortems.json")

print("Loading data from JSON...")
with open(data_path, "r") as f:
    incidents = json.load(f).get("incidents", [])

documents = []
metadata = []
ids = []

print("Structuring documents for embedding...")
for idx, incident in enumerate(incidents):
    # The 'document' is the string text that will be converted into a vector
    doc_text = (
        f"Title: {incident['title']}\n"
        f"Symptoms: {incident['symptoms']}\n"
        f"Root Cause: {incident['root_cause']}\n"
        f"Resolution: {incident['resolution']}"
    )
    documents.append(doc_text)

    # Metadata remains attached to the vector for filtering and final JSON output
    metadata.append({
        "incident_id": incident["incident_id"],
        "title": incident["title"],
        "root_cause": incident["root_cause"],
        "resolution": incident["resolution"]
    })

    ids.append(idx + 1)

print(
    f"Embedding and uploading {len(documents)} documents to Qdrant (this may take a moment on the first run as the model downloads)...")

# client.add() automatically chunks, embeds via FastEmbed, and inserts the vectors
client.add(
    collection_name=collection_name,
    documents=documents,
    metadata=metadata,
    ids=ids
)

print(f"Success! Knowledge base '{collection_name}' is fully loaded and ready for RAG.")