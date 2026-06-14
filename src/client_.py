from openai import AsyncOpenAI

from .config import LLM_API_KEY, LLM_BASE_URL

client = AsyncOpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)
