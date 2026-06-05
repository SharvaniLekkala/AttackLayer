from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")

CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL")

EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL")

DATABASE_URL = os.getenv("DATABASE_URL")

CHROMA_PATH = os.getenv("CHROMA_PATH")