import asyncio
import time

from agentflow import tool


@tool
async def researcher_a(topic: str) -> str:
    await asyncio.sleep(2)
    return f"Source A: information about {topic}"


@tool
async def researcher_b(topic: str) -> str:
    await asyncio.sleep(2)
    return f"Source B: information about {topic}"


async def main():

    start = time.perf_counter()

    results = await asyncio.gather(
        researcher_a.execute(
            topic="multi-agent AI"
        ),
        researcher_b.execute(
            topic="multi-agent AI"
        ),
    )

    elapsed = time.perf_counter() - start

    print("\n========== RESULTS ==========\n")

    for result in results:
        print(result)

    print(
        f"\nExecution time: {elapsed:.2f} seconds"
    )

    if elapsed < 3:
        print(
            "\nPASS: tools executed in parallel."
        )
    else:
        print(
            "\nFAIL: tools appear to be sequential."
        )


if __name__ == "__main__":
    asyncio.run(main())
