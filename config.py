
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)


def get_api_key(name: str) -> str | None:
    try:
        value = st.secrets.get(name)
    except FileNotFoundError:
        value = None

    if isinstance(value, str) and value.strip():
        return value.strip()

    return (os.getenv(name) or "").strip() or None


GOOGLE_API_KEY = get_api_key("GOOGLE_API_KEY")
GROQ_API_KEY = get_api_key("GROQ_API_KEY")

GROQ_MODEL = "openai/gpt-oss-120b"
# The LangChain client sends retrieval task types with embedding requests.
EMBEDDING_MODEL = "gemini-embedding-001"

DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
VECTOR_DIR = DATA_DIR / "chroma_db"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_UPLOAD_MB = 20
