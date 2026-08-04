# Automated SRE Incident Responder

An AI-driven, microservice-based Site Reliability Engineering (SRE) agent designed to autonomously analyze incoming system alerts and recommend immediate root-cause resolutions. 

This project is built using an Agentic RAG architecture and enforces strict structured outputs (JSON) to seamlessly integrate into automated DevOps and incident management pipelines.

## 🚀 Tech Stack
* **Framework:** FastAPI (Python)
* **AI Engine:** Groq API (`llama-3.1-8b-instant`) for ultra-low latency inference
* **Data Validation:** Pydantic (Strict JSON enforcement)
* **Observability:** Langfuse (Execution tracing, latency tracking, and prompt monitoring)
* **Infrastructure:** Docker (Sandboxed containerization)

## 🔒 Security & Architecture highlights
* **Principle of Least Privilege:** The application runs as a dedicated, non-root user (`sre_agent`) inside the Docker container to prevent host-system compromise in the event of an LLM prompt injection attack.
* **12-Factor App Methodology:** Environment-agnostic codebase utilizing dedicated `.env.dev` files to strictly separate development and production API keys.
* **Modular Design:** Separation of concerns across API routing, LLM service logic, and prompt templating.

## 🛠️ Local Setup & Deployment

### 1. Environment Variables
Create a `.env.dev` file in the root directory and add your API keys:
```env
GROQ_API_KEY=your_groq_key
LANGFUSE_SECRET_KEY=your_langfuse_secret
LANGFUSE_PUBLIC_KEY=your_langfuse_public
LANGFUSE_BASE_URL=[https://cloud.langfuse.com](https://cloud.langfuse.com)
LANGFUSE_HOST=[https://cloud.langfuse.com](https://cloud.langfuse.com)
MODEL_NAME=llama-3.1-8b-instant
MODEL_TEMPERATURE=0.0