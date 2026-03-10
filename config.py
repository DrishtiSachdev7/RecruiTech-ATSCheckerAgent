"""Configuration from environment. Copy .env.example to .env and set values."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load from .env in project root
load_dotenv(Path(__file__).resolve().parent / ".env")

# --- LLM (OpenAI)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- Kafka
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_INPUT_TOPIC = os.getenv("KAFKA_INPUT_TOPIC", "recruitech.scoring.input")
KAFKA_OUTPUT_TOPIC = os.getenv("KAFKA_OUTPUT_TOPIC", "recruitech.scoring.output")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "recruitech-scoring-agent")

# --- AWS (for resume from S3)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
# Optional: use IAM role instead of keys when running on AWS

# --- Optional: max tokens for LLM response (keep low to save cost)
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))
