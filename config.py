from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in .env file.")

OPENAI_EMBEDDER = "text-embedding-3-small"
OPENAI_MODEL = "gpt-4o-mini"
