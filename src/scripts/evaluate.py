import json
from openai import OpenAI
from src.core.config import settings
from src.agent.orchestrator import run_sre_agent
from src.agent.tools import get_live_metrics, search_past_incidents, get_recent_logs
from src.prompts.sre_prompts import EVAL_SYSTEM_PROMPT

# Initialize the Judge LLM
judge_client = OpenAI(api_key=settings.OPENAI_API_KEY)
JUDGE_MODEL = settings.JUDGE_MODEL_NAME


def run_evaluation():
    test_alert = "PagerDuty Alert: The payment-gateway service is dropping connections and throwing 500 errors. Customers cannot check out."
    service = "payment-gateway"

    print("⏳ Running SRE Agent (This may take a few seconds)...")
    agent_output = run_sre_agent(test_alert)

    print("\n🔍 Fetching deterministic context for the Judge...")
    # We grab the exact deterministic data the agent saw
    metrics = get_live_metrics(service)
    logs = get_recent_logs(service)
    past_incidents = search_past_incidents("payment-gateway dropping connections 500 errors")

    source_context = f"METRICS:\n{metrics}\n\nLOGS:\n{logs}\n\nPAST INCIDENTS:\n{past_incidents}"

    judge_user_prompt = f"SOURCE CONTEXT:\n{source_context}\n\nAGENT OUTPUT:\n{agent_output}"

    print("⚖️  Submitting to LLM Judge...")
    response = judge_client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {"role": "system", "content": EVAL_SYSTEM_PROMPT},
            {"role": "user", "content": judge_user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )

    eval_result = json.loads(response.choices[0].message.content)

    print("\n" + "=" * 50)
    print("🏆 EVALUATION RESULTS")
    print("=" * 50)
    print(f"Faithfulness Score:  {eval_result['faithfulness_score']} / 1.0")
    print(f"Answer Relevance:    {eval_result['relevance_score']} / 1.0")
    print("-" * 50)
    print(f"Judge Reasoning:\n{eval_result['reasoning']}")
    print("=" * 50)

    # Threshold logic for Day 7 CI/CD
    if eval_result['faithfulness_score'] < 0.85 or eval_result['relevance_score'] < 0.9:
        print("❌ EVALUATION FAILED: Scores did not meet the 0.85 & 0.90 threshold.")
        exit(1)
    else:
        print("✅ EVALUATION PASSED: Agent meets production standards.")
        exit(0)


if __name__ == "__main__":
    run_evaluation()
