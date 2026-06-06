import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai:gpt-4o")
APP_TITLE = "Deep Agents — Enhanced"
APP_ICON = "🧠"
WATERMARK_TEXT = "Made by Prathamesh Mishra"

AVAILABLE_MODELS = [
    {"id": "openai:gpt-4o", "label": "GPT-4o", "provider": "openai"},
    {"id": "openai:gpt-4o-mini", "label": "GPT-4o Mini", "provider": "openai"},
    {"id": "openai:gpt-4-turbo", "label": "GPT-4 Turbo", "provider": "openai"},
    {"id": "groq:llama-3.3-70b-versatile", "label": "Llama 3.3 70B", "provider": "groq"},
    {"id": "groq:qwen-qwq-32b", "label": "Qwen QwQ 32B", "provider": "groq"},
    {"id": "groq:gemma2-9b-it", "label": "Gemma 2 9B", "provider": "groq"},
]

MAX_HISTORY_CONVERSATIONS = 50
MAX_MESSAGES_PER_CONVERSATION = 200
