import os
from pathlib import Path


def load_environment():
    """If there is a .env.local file, load it."""

    env_local = Path(".env.local")
    if env_local.exists():
        from dotenv import load_dotenv

        load_dotenv(".env.local")
    else:
        print(".env.local file not found, loading from secrets.")


def get_secret(key: str) -> str:
    try:
        value = os.getenv(key)
        if value is None:
            print(f"Secret {key} not found in environment variables")
            return None

        print(f"Raw value length: {len(value)}")
        print(f"Raw value repr: {repr(value)}")  # This will show any \n
        return value.strip()
    except Exception as e:
        print(f"Error accessing secret {key}: {e}")
        return None


load_environment()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
