#!/usr/bin/env python3
"""
Example script demonstrating how to use the LlamaSearch AI client.
"""

import asyncio
import os

from llamasearchai.client import Client
from loguru import logger


async def search_example(client: Client) -> None:
    """Run an example search query."""
    logger.info("Running search example...")

    # Perform a search
    search_results = await client.search(
        query="python fastapi tutorial",
        num_results=5,
        providers=["google", "bing"],
    )

    logger.info(f"Found {len(search_results['results'])} results")
    logger.info(f"Top result: {search_results['results'][0]['title']}")

    # Print metadata
    logger.info(
        f"Search processing time: {search_results['metadata']['processing_time']:.2f}s"
    )
    logger.info(
        f"Engines used: {', '.join(search_results['metadata']['engines_used'])}"
    )


async def vector_example(client: Client) -> None:
    """Run example vector operations."""
    logger.info("Running vector example...")

    # Create embeddings
    texts = [
        "Python is a programming language",
        "FastAPI is a modern web framework",
        "Vector databases store embeddings for similarity search",
    ]

    embed_response = await client.embed(texts=texts)

    logger.info(f"Created {len(embed_response['embeddings'])} embeddings")
    logger.info(f"Embedding dimensions: {embed_response['metadata']['dimensions']}")

    # Add vectors to a collection
    vectors = []
    for i, embedding in enumerate(embed_response["embeddings"]):
        vectors.append(
            {
                "id": f"doc{i}",
                "vector": embedding["vector"],
                "metadata": {
                    "text": embedding["text"],
                    "source": "example",
                },
            }
        )

    upsert_response = await client.upsert_vectors(
        collection="example_collection",
        vectors=vectors,
        create_collection=True,
    )

    logger.info(f"Inserted {upsert_response['inserted_count']} vectors")

    # Search for similar vectors
    search_response = await client.vector_search(
        query="modern web development",
        collection="example_collection",
        num_results=2,
    )

    logger.info(f"Found {len(search_response['results'])} similar vectors")
    for result in search_response["results"]:
        logger.info(
            f"Result {result['id']} with score {result['score']}: {result['metadata'].get('text', '')}"
        )


async def personalization_example(client: Client) -> None:
    """Run example personalization operations."""
    logger.info("Running personalization example...")

    # Get user profile
    user_id = "example_user"
    profile = await client.get_user_profile(user_id)

    logger.info(f"User profile: {user_id}")
    logger.info(f"Topics of interest: {', '.join(profile['topics_of_interest'])}")

    # Personalize content
    search_results = [
        {
            "id": "result1",
            "title": "Introduction to Python",
            "url": "https://example.com/python-intro",
            "score": 0.95,
        },
        {
            "id": "result2",
            "title": "Advanced JavaScript Techniques",
            "url": "https://example.com/js-advanced",
            "score": 0.92,
        },
        {
            "id": "result3",
            "title": "Machine Learning with Python",
            "url": "https://example.com/ml-python",
            "score": 0.88,
        },
    ]

    personalized = await client.personalize(
        user_id=user_id,
        content=search_results,
        context={"query": "programming tutorials"},
    )

    logger.info("Personalized results:")
    for item in personalized["content"]:
        logger.info(f"{item['title']} - Score: {item['score']:.2f}")

    # Submit feedback
    feedback = await client.send_feedback(
        user_id=user_id,
        item_id="result1",
        rating=4.5,
        feedback_text="Very helpful for beginners",
    )

    logger.info(f"Feedback status: {feedback['status']}")


async def main() -> None:
    """Run all examples."""
    # Create a client
    client = Client(
        api_key=os.environ.get("LLAMASEARCH_API_KEY", "your-api-key"),
        base_url=os.environ.get("LLAMASEARCH_API_URL", "http://localhost:8000"),
    )

    # Run examples
    await search_example(client)
    print("\n" + "-" * 50 + "\n")

    await vector_example(client)
    print("\n" + "-" * 50 + "\n")

    await personalization_example(client)


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg),
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
        level="INFO",
    )

    # Run the examples
    asyncio.run(main())
