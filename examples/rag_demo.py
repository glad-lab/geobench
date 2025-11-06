"""Simple demonstration of RAG package with real components.

This example demonstrates the new RAG package with a minimal setup.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

load_dotenv()


def main():
    """Demonstrate basic RAG pipeline."""
    print("\n" + "=" * 80)
    print("RAG Package Demonstration")
    print("=" * 80)

    from rag import RAGPipeline, VectorRetriever, LLMGenerator, ConsoleObserver
    from vector_store import VectorStoreManager
    from llm import create_llm_client

    # Initialize components
    print("\n1. Initializing components...")

    vector_store = VectorStoreManager(
        collection_name="adversarial_seo",
        embedding_provider="gemini",
        reset_collection=False,
    )

    llm_client = create_llm_client(
        provider=os.getenv("API_PROVIDER", "anthropic"),
        model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
    )

    # Build pipeline
    print("2. Building RAG pipeline with observability...")

    pipeline = (
        RAGPipeline()
        .with_retriever(VectorRetriever(vector_store))
        .with_generator(LLMGenerator(llm_client, temperature=0.0, max_tokens=500))
        .with_observability(ConsoleObserver(verbose=True))
    )

    # Execute query
    print("\n3. Executing query...\n")

    query = "What is the best camera for professional photography?"
    result = pipeline.query(query)

    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    print(f"\nQuery: {result.query}")
    print(f"\nMetrics:")
    print(f"  - Documents retrieved: {result.num_retrieved}")
    print(f"  - Retrieval time: {result.retrieval_time:.3f}s")
    print(f"  - Generation time: {result.generation_time:.3f}s")
    print(f"  - Total time: {result.total_time:.3f}s")

    print(f"\nTop Retrieved Documents:")
    for i, doc in enumerate(result.retrieved_docs[:5], 1):
        print(f"  {i}. {doc.get('name', 'Unknown')}")
        print(f"     Score: {doc.get('retrieval_score', 'N/A'):.4f}")
        if doc.get("price"):
            print(f"     Price: ${doc.get('price')}")

    print(f"\nGenerated Response:")
    print(f"{result.generated_response}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback

        traceback.print_exc()
