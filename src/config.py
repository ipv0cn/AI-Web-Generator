import os

from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_API_BASE_URL", "https://api.deepseek.com")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL_NAME", "deepseek-chat")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
