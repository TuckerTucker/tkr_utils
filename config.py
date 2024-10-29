from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in .env file.")

OPENAI_MODEL = "gpt-4o-mini"
OPENAI_EMBEDDER = "text-embedding-3-small"



# Anthropic

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if ANTHROPIC_API_KEY is None:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file.")

ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

# Rate limiting parameters for batch processing.
MAX_REQUESTS_PER_MINUTE: float = float(os.getenv("MAX_REQUESTS_PER_MINUTE", 60))
MAX_TOKENS_PER_MINUTE: float = float(os.getenv("MAX_TOKENS_PER_MINUTE", 1000))
MAX_ATTEMPTS: int = int(os.getenv("MAX_ATTEMPTS", 3))
