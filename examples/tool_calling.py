import asyncio
import time

from agentflow import tool


@tool
async def researcher_a(topic: str) -> str:
    """Simulates research source A."""
    await asyncio.sleep(2)

    return f"Source A: information about {topic}"


@tool
async def researcher_b(topic: str) -> str:
    """Simulates research source B."""
    await asyncio.sleep(2)

    return f"Source B: information about {topic}"


async def main():

    print("Starting parallel tool execution...")

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

    print()
    print("========== RESULTS ==========")
    print()

    for result in results:
        print(result)

    print()
    print(
        f"Execution time: {elapsed:.2f} seconds"
    )

    print()

    if elapsed < 3:
        print(
            "PASS: Tools executed in parallel."
        )
    else:
        print(
            "FAIL: Tools appear to be sequential."
        )


if __name__ == "__main__":
    asyncio.run(main())
