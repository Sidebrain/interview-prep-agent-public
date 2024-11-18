import asyncio
from app.agents.agent_v2 import Memory, MockInterview, Thinker


async def main():
    m = MockInterview(
        thinker=Thinker(),
        memory=Memory(memory_topic="mock_interview"),
    )
    await m.extract_questions_and_rubric_params(file_path="./config/artifacts.yaml")


if __name__ == "__main__":
    asyncio.run(main())
