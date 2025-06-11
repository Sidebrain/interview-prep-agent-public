import asyncio
import logging
import os
from collections import defaultdict
from pprint import pprint

from pydantic import BaseModel, Field

from app.event_agents.orchestrator.thinker import Thinker

logger = logging.getLogger(__name__)


class Ranker:
    def __init__(self) -> None:
        self.interviews: list[dict[str, str]] = self.load_interviews()
        self.ranking: dict[str, list[int]] = {}
        self.pairwise_comparisons: dict[frozenset[str], list[str]] = (
            defaultdict(list)
        )

    def load_interviews(self) -> list[dict[str, str]]:
        interviews = []
        for file in os.listdir("config/interviews"):
            with open(f"config/interviews/{file}", "r") as f:
                interviews.append({file: f.read()})
        logger.debug(
            f"Loaded {len(interviews)} interviews",
            extra={
                "context": {
                    "interviews": {
                        filename: len(content)
                        for i in interviews
                        for filename, content in i.items()
                    }
                }
            },
        )
        return interviews

    async def ai_comparator(
        self, left: dict[str, str], right: dict[str, str]
    ) -> list[dict]:
        # Get the keys for the interviews
        left_key = next(iter(left.keys()))
        right_key = next(iter(right.keys()))

        # Check if we already have this comparison
        pair = frozenset([left_key, right_key])
        if pair in self.pairwise_comparisons:
            previous_results = self.pairwise_comparisons[pair]
            # Use majority vote if we have multiple comparisons
            if previous_results:
                better = max(
                    set(previous_results), key=previous_results.count
                )
                return type(
                    "Comparison",
                    (),
                    {
                        "better": better,
                        "worse": left_key
                        if better == right_key
                        else right_key,
                    },
                )()

        class Comparison(BaseModel):
            better: str = Field(
                description="The interview that is better"
            )
            worse: str = Field(
                description="The interview that is worse"
            )
            reason: str = Field(
                description="The reason for the better interview"
            )

        t = Thinker()
        messages = [
            {
                "role": "system",
                "content": f"""
                You are to compare the two interviews, and choose the one that is better on the following evaluation criteria: {"understanding of frontend development"}
                """,
            },
            {
                "role": "user",
                "content": f"Compare the following two interviews:\n-----interview 1-----\n{left.values()}\n-----interview 2-----\n{right.values()}",
            },
        ]
        response = await t.extract_structured_response(
            Comparison, messages, debug=True
        )
        if response is None:
            raise ValueError("No response from AI")

        # Store the result
        self.pairwise_comparisons[pair].append(response.better)
        return response

    async def merge_sort(
        self, arr: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left = arr[:mid]
        right = arr[mid:]

        # Process both halves concurrently
        left_sorted, right_sorted = await asyncio.gather(
            self.merge_sort(left), self.merge_sort(right)
        )
        return await self.merge(left_sorted, right_sorted)

    async def merge(
        self, left: list[dict[str, str]], right: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        result = []
        i = j = 0
        comparison_tasks = []

        # Prepare batches of comparisons
        while i < len(left) and j < len(right):
            comparison_tasks.append(
                self.ai_comparator(left[i], right[j])
            )
            i += 1
            j += 1

        # Reset indices for processing results
        i = j = 0

        # Process comparisons concurrently
        if comparison_tasks:
            comparisons = await asyncio.gather(*comparison_tasks)

            # Process the comparison results
            for comparison in comparisons:
                left_key = next(iter(left[i].keys()))
                right_key = next(iter(right[j].keys()))

                if comparison.better == left_key:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1

        # Append remaining elements
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    async def rank(self) -> list[dict[str, str]]:
        sorted_interviews = await self.merge_sort(self.interviews)
        # Store rankings as indices (0 is highest rank)
        self.ranking = {
            next(iter(interview.keys())): rank
            for rank, interview in enumerate(sorted_interviews)
        }
        pprint(self.ranking)
        return sorted_interviews


if __name__ == "__main__":
    ranker = Ranker()
    asyncio.run(ranker.rank())
