from app.services.llms.openai_client import openai_async_client


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
