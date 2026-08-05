import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load dev environment variables
load_dotenv(".env.dev")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model_name = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")

PROMPT = """
You are an expert Site Reliability Engineer. 
Generate 15 realistic synthetic incident post-mortems for a microservices architecture.

CRITICAL INSTRUCTION:
Output ONLY a JSON object containing a single key "incidents".
The value must be an array of exactly 15 objects with these exact keys:
- "incident_id": A string (e.g., "INC-001")
- "title": A short string describing the outage
- "symptoms": What the monitoring system alerted on
- "root_cause": The underlying technical issue
- "resolution": How the engineering team fixed it
"""

print(f"Generating 15 synthetic SRE post-mortems using {model_name}...")

response = client.chat.completions.create(
    model=model_name,
    messages=[{"role": "user", "content": PROMPT}],
    response_format={"type": "json_object"},
    temperature=0.7
)

raw_json = response.choices[0].message.content
data = json.loads(raw_json)

# Save to the data directory
output_path = os.path.join("data", "post_mortems.json")
with open(output_path, "w") as f:
    json.dump(data, f, indent=4)

print(f"Successfully generated and saved 15 incidents to {output_path}!")