import os
from dotenv import load_dotenv

# Load environment variables from .env.dev if present
load_dotenv(".env.dev")

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LANGFUSE_SECRET_KEY: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    LANGFUSE_PUBLIC_KEY: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_BASE_URL: str = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
    LANGFUSE_HOST: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Model
    AGENT_MODEL_NAME: str = os.getenv("AGENT_MODEL_NAME", "llama-3.3-70b-versatile")
    JUDGE_MODEL_NAME: str = os.getenv("JUDGE_MODEL_NAME", "gpt-4o")


settings = Settings()
