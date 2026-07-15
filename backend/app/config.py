import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"

# LLM_PROVIDER selects which OpenAI-compatible endpoint app/agent/llm.py talks
# to. Both providers are hit through the same `openai` SDK client — only the
# base_url, api_key, and model differ.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower()

if LLM_PROVIDER == "groq":
    LLM_API_KEY = GROQ_API_KEY
    LLM_BASE_URL = GROQ_BASE_URL
    LLM_MODEL = os.getenv("MODEL", GROQ_DEFAULT_MODEL)
else:
    LLM_API_KEY = OPENROUTER_API_KEY
    LLM_BASE_URL = OPENROUTER_BASE_URL
    LLM_MODEL = os.getenv("MODEL", OPENROUTER_DEFAULT_MODEL)

BACKEND_DIR = Path(__file__).resolve().parent.parent
FARE_RULES_DIR = BACKEND_DIR / "data" / "fare_rules"
CHROMA_DIR = BACKEND_DIR / "data" / "chroma"
CHROMA_COLLECTION = "fare_rules"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# PRD section 7 — autonomous decision boundary
ESCALATE_ABOVE_AMOUNT = 500.0
ESCALATE_BELOW_CONFIDENCE = 0.70
ESCALATE_BELOW_RETRIEVAL_SCORE = 0.45
