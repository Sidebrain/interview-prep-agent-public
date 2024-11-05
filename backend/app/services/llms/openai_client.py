import openai
import os

from app.services.env_keys import OPENAI_API_KEY

# # from dotenv import load_dotenv

# # load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# def get_secret(key: str) -> str:
#     try:
#         value = os.getenv(key)
#         print(f"Raw value length: {len(value)}")
#         print(f"Raw value repr: {repr(value)}")  # This will show any \n
#         return value.strip() if value else None
#     except Exception as e:
#         print(f"Error accessing secret {key}: {e}")
#         return None


# Initialize the OpenAI client with better error handling
def create_openai_client() -> openai.AsyncClient:
    api_key = OPENAI_API_KEY

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables or secrets")

    print(
        f"Creating OpenAI client with API key: {'*' * len(api_key)}"
    )  # Log masked key length for debugging

    return openai.AsyncClient(
        api_key=api_key,
    )


# Create the client
try:
    openai_async_client = create_openai_client()
except Exception as e:
    print(f"Failed to create OpenAI client: {e}")
    raise

# openai_async_client = openai.AsyncClient(
#     api_key=OPENAI_API_KEY,
# )
