import openai
import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_async_client = openai.AsyncClient(
    api_key=OPENAI_API_KEY,
)


async def get_base_response():
    response = await openai_async_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the meaning of life per Kant?"},
        ],
        model="gpt-4o",
    )
    return response


if __name__ == "__main__":
    import asyncio
    response = asyncio.run(get_base_response())
    print(response.choices[0].message.content)
