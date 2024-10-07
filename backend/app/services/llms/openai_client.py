import openai
import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_async_client = openai.AsyncClient(
    api_key=OPENAI_API_KEY,
)
