"""
Central config for StayIntel LLM (env-based).
"""
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

# Database URL for SQLAlchemy engine (PostgreSQL recommended in production).
DATABASE_URL = os.getenv("DATABASE_URL")
