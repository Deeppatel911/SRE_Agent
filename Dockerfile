# Use a lightweight, official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (leverages Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/
COPY .env.dev .env.dev

# --- LEAST PRIVILEGE SECURITY ---
# Create a non-root user and switch to it
RUN useradd -m sre_agent
USER sre_agent

# Expose the FastAPI port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]