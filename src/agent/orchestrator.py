import os
import json
from groq import Groq
from langfuse import observe
from .tools import search_past_incidents, get_live_metrics, get_recent_logs
from src.core.config import settings
from src.prompts.sre_prompts import AGENT_SYSTEM_PROMPT

# Initialize the Groq client
client = Groq(api_key=settings.GROQ_API_KEY)
model_name = settings.AGENT_MODEL_NAME


# ---------------------------------------------------------
# Tool Definitions: Translating Pydantic to Groq's JSON Schema
# ---------------------------------------------------------
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "search_past_incidents",
            "description": "Searches the local Qdrant database for similar past SRE incidents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The semantic search query describing the current incident symptoms."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_live_metrics",
            "description": "Fetches real-time CPU, Memory, and Error Rate metrics for a given internal microservice.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "The name of the internal microservice to query (e.g., 'payment-gateway', 'auth-service')."
                    }
                },
                "required": ["service_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_logs",
            "description": "Fetches recent server error logs and stack traces for a given microservice.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "The name of the internal microservice to query."
                    }
                },
                "required": ["service_name"]
            }
        }
    }
]

# Map tool names to their actual Python function references
available_tools = {
    "search_past_incidents": search_past_incidents,
    "get_live_metrics": get_live_metrics,
    "get_recent_logs": get_recent_logs,
}


# ---------------------------------------------------------
# The Agentic Loop
# ---------------------------------------------------------
@observe()  # Langfuse trace wraps the entire agent execution
def run_sre_agent(incident_alert: str) -> str:
    print(f"\n🚨 ALERT RECEIVED: {incident_alert}")

    messages = [
        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
        {"role": "user", "content": incident_alert}
    ]

    # We use a loop to allow the agent to call multiple tools sequentially if needed.
    # Capping at 5 iterations prevents infinite loops if the model gets stuck.
    for iteration in range(5):
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools_schema,
            tool_choice="auto",
            temperature=0.0  # Strict determinism for diagnostics
        )

        response_message = response.choices[0].message
        messages.append(response_message)

        # Base Case: The model did not call a tool, meaning it is ready to answer.
        if not response_message.tool_calls:
            print("\n✅ Agent has completed its diagnosis.")
            return response_message.content

        # Recursive Case: The model wants to execute tools.
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"🧠 Agent Logic -> Calling '{function_name}' with {function_args}")

            # Dynamically execute the requested tool
            tool_to_execute = available_tools.get(function_name)
            if tool_to_execute:
                function_result = tool_to_execute(**function_args)
            else:
                function_result = f"CRITICAL: Tool {function_name} does not exist."

            # Append the raw data from the tool back into the conversation thread
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": str(function_result)
            })

    return "SYSTEM ERROR: Agent exceeded maximum allowed iterations without reaching a conclusion."
