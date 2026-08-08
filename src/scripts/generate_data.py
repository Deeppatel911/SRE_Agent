import os
import json
from groq import Groq
from src.core.config import settings
from src.prompts import DATA_GENERATION_PROMPT

client = Groq(settings.GROQ_API_KEY)
model_name = settings.MODEL_NAME


print(f"Generating 15 synthetic SRE post-mortems using {model_name}...")

response = client.chat.completions.create(
    model=model_name,
    messages=[{"role": "user", "content": DATA_GENERATION_PROMPT}],
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