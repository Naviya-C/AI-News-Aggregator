from openai import OpenAI
from app.core.config import OPEN_AI_KEY

open_ai_client = OpenAI(api_key = OPEN_AI_KEY)