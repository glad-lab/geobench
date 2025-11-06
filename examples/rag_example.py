"""Example demonstrating RAG package usage.

This example shows how to use the RAG package for adversarial SEO research.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

load_dotenv()


def example_basic_pipeline():
    """Example 1: Basic RAG pipeline with vector retrieval and LLM generation."""
    print("\n" + "=" * 80)
    print("Example 1: Basic RAG Pipeline")
    print("=" * 80)

    from rag import RAGPipeline, VectorRetriever, LLMGenerator, ConsoleObserver
    from vector_store import VectorStoreManager
    from llm import create_llm_client

    # Initialize components
    vector_store = VectorStoreManager(
        collection_name="adversarial_seo", embedding_provider="gemini"
    )

    llm_client = create_llm_client(
        provider=os.getenv("API_PROVIDER", "anthropic"),
        model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
    )

    # Build pipeline
    pipeline = (
        RAGPipeline()
        .with_retriever(VectorRetriever(vector_store))
        .with_generator(LLMGenerator(llm_client))
        .with_observability(ConsoleObserver(verbose=True))
    )

    # Execute query
    result = pipeline.query("best camera for professional photography")

    # Display results
    print(f"\nQuery: {result.query}")
    print(f"Retrieved {result.num_retrieved} documents in {result.retrieval_time:.3f}s")
    print(f"Generated response in {result.generation_time:.3f}s")
    print(f"\nResponse:\n{result.generated_response}")


def example_hybrid_retrieval():
    """Example 2: Hybrid retrieval with vector search + LLM reranking."""
    print("\n" + "=" * 80)
    print("Example 2: Hybrid Retrieval with Reranking")
    print("=" * 80)

    from rag import RAGPipeline, HybridRetriever, LLMGenerator
    from vector_store import VectorStoreManager
    from llm import create_llm_client
    from ranking import create_ranker

    # Initialize components
    vector_store = VectorStoreManager(collection_name="adversarial_seo")
    llm_client = create_llm_client(provider="anthropic")

    # Create reranker for hybrid retrieval
    reranker = create_ranker("llm", llm_client=llm_client)

    # Build pipeline with hybrid retrieval
    pipeline = (
        RAGPipeline()
        .with_retriever(
            HybridRetriever(
                vector_store=vector_store,
                reranker=reranker,
                retrieval_k=20,  # Retrieve 20 candidates
                rerank_k=5,  # Rerank to top 5
            )
        )
        .with_generator(LLMGenerator(llm_client))
    )

    # Execute query
    result = pipeline.query("affordable camera under $500")

    print(f"\nQuery: {result.query}")
    print(f"Retrieved {result.num_retrieved} documents")
    print(f"Final documents used: {result.num_final}")
    print(f"\nTop retrieved documents:")
    for i, doc in enumerate(result.final_docs[:3], 1):
        print(f"  {i}. {doc.get('name', 'Unknown')}")
        if "rerank_score" in doc:
            print(f"     Rerank score: {doc['rerank_score']:.3f}")


def example_observability():
    """Example 3: Using observability features."""
    print("\n" + "=" * 80)
    print("Example 3: Observability and Metrics")
    print("=" * 80)

    from rag import (
        RAGPipeline,
        VectorRetriever,
        LLMGenerator,
        ConsoleObserver,
        StructuredLogger,
        MetricsCollector,
    )
    from vector_store import VectorStoreManager
    from llm import create_llm_client

    # Initialize components
    vector_store = VectorStoreManager(collection_name="adversarial_seo")
    llm_client = create_llm_client(provider="anthropic")

    # Create multiple observers
    console_observer = ConsoleObserver(verbose=True)
    metrics_collector = MetricsCollector()
    log_file = "/tmp/rag_pipeline.log"
    file_logger = StructuredLogger(log_file)

    # Build pipeline with multiple observers
    pipeline = (
        RAGPipeline()
        .with_retriever(VectorRetriever(vector_store))
        .with_generator(LLMGenerator(llm_client))
        .with_observability(console_observer)
        .with_observability(metrics_collector)
        .with_observability(file_logger)
    )

    # Execute multiple queries
    queries = [
        "best camera for wildlife photography",
        "budget laptop for programming",
        "kitchen appliances for baking",
    ]

    for query in queries:
        result = pipeline.query(query)
        print(f"\nProcessed: {query}")

    # Display metrics summary
    print("\n" + "=" * 80)
    print("Metrics Summary")
    print("=" * 80)

    summary = metrics_collector.get_summary()
    print(f"Total queries: {summary['total_queries']}")
    print(f"Avg retrieval time: {summary['avg_retrieval_time']:.3f}s")
    print(f"Avg generation time: {summary['avg_generation_time']:.3f}s")
    print(
        f"Avg documents retrieved: {summary['avg_documents_retrieved']:.1f}"
    )

    print(f"\nLogs written to: {log_file}")


def example_custom_prompts():
    """Example 4: Customizing system prompts and templates."""
    print("\n" + "=" * 80)
    print("Example 4: Custom Prompts")
    print("=" * 80)

    from rag import RAGPipeline, VectorRetriever, LLMGenerator
    from vector_store import VectorStoreManager
    from llm import create_llm_client

    # Initialize components
    vector_store = VectorStoreManager(collection_name="adversarial_seo")
    llm_client = create_llm_client(provider="anthropic")

    # Custom system prompt
    custom_system_prompt = """You are a product recommendation expert specializing in photography equipment.
Provide detailed, technical recommendations based on the retrieved product information.
Focus on image quality, sensor specifications, and value for money."""

    # Custom user template
    custom_user_template = """User Question: {query}

Available Products:
{documents}

Please provide a detailed recommendation with technical justification."""

    # Build pipeline with custom prompts
    pipeline = (
        RAGPipeline()
        .with_retriever(VectorRetriever(vector_store))
        .with_generator(
            LLMGenerator(
                llm_client,
                system_prompt=custom_system_prompt,
                user_template=custom_user_template,
                temperature=0.3,  # More creative responses
            )
        )
    )

    # Execute query
    result = pipeline.query("professional camera for landscape photography")

    print(f"\nQuery: {result.query}")
    print(f"\nCustom Response:\n{result.generated_response}")


def example_attack_detection():
    """Example 5: Using RAG pipeline for attack detection."""
    print("\n" + "=" * 80)
    print("Example 5: Attack Detection")
    print("=" * 80)

    from rag import RAGPipeline, VectorRetriever, LLMGenerator
    from vector_store import VectorStoreManager
    from llm import create_llm_client

    # Initialize components
    vector_store = VectorStoreManager(collection_name="adversarial_seo")
    llm_client = create_llm_client(provider="anthropic")

    # Build pipeline
    pipeline = (
        RAGPipeline()
        .with_retriever(VectorRetriever(vector_store))
        .with_generator(LLMGenerator(llm_client))
    )

    # Execute query
    result = pipeline.query("best camera for photography")

    # Analyze retrieved documents for attacks
    print(f"\nQuery: {result.query}")
    print(f"\nRetrieved Documents Analysis:")

    attack_count = 0
    for i, doc in enumerate(result.retrieved_docs, 1):
        # Check for attack indicators
        is_attack = (
            doc.get("___attack_type")
            or doc.get("__attack_type")
            or doc.get("_is_attack_document")
        )

        if is_attack:
            attack_count += 1
            attack_type = doc.get("___attack_type") or doc.get("__attack_type", "unknown")
            print(f"  {i}. {doc.get('name', 'Unknown')} - ATTACK DETECTED ({attack_type})")
            print(f"     Retrieval score: {doc.get('retrieval_score', 'N/A')}")
        else:
            print(f"  {i}. {doc.get('name', 'Unknown')} - Clean")

    print(f"\nAttack Detection Summary:")
    print(f"  Total documents retrieved: {result.num_retrieved}")
    print(f"  Attack documents detected: {attack_count}")
    print(
        f"  Attack rate: {attack_count / result.num_retrieved * 100:.1f}%"
        if result.num_retrieved > 0
        else "  Attack rate: N/A"
    )


def main():
    """Run all examples."""
    examples = [
        ("Basic Pipeline", example_basic_pipeline),
        ("Hybrid Retrieval", example_hybrid_retrieval),
        ("Observability", example_observability),
        ("Custom Prompts", example_custom_prompts),
        ("Attack Detection", example_attack_detection),
    ]

    print("\n" + "=" * 80)
    print("RAG Package Examples")
    print("=" * 80)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    try:
        choice = input("\nSelect example (1-5, or 'all'): ").strip().lower()

        if choice == "all":
            for _, func in examples:
                func()
                input("\nPress Enter to continue to next example...")
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            examples[int(choice) - 1][1]()
        else:
            print("Invalid choice")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted")
    except Exception as e:
        print(f"\n\nError running example: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
