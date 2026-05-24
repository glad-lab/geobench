"""Example demonstrating RAG package usage.

This example shows how to use the RAG package for adversarial SEO research.
Auto-populates the vector database if empty.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

load_dotenv()


def ensure_database_populated():
    """Ensure vector database is populated before running examples."""
    print("\n" + "=" * 80)
    print("Database Check")
    print("=" * 80)

    from vector_store import VectorStoreManager

    # Get embedding provider from .env
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "gemini")

    vector_store = VectorStoreManager(
        collection_name="adversarial_seo",
        embedding_provider=embedding_provider
    )

    stats = vector_store.get_collection_stats()
    doc_count = stats.get('points_count', 0)

    print(f"Collection 'adversarial_seo' has {doc_count} documents")

    if doc_count == 0:
        print("\n⚠️  Database is empty! Populating with product data...")
        print("This may take a few minutes...")

        import json
        import time

        # Load products
        data_path = Path(__file__).parent.parent / "data" / "products_master.json"

        if not data_path.exists():
            print(f"❌ Error: Product data not found at {data_path}")
            print("Please ensure data/products_master.json exists")
            sys.exit(1)

        with open(data_path, 'r') as f:
            data = json.load(f)

        # Convert to flat list
        products = []
        for category_name, category_items in data.items():
            for item in category_items:
                item['category'] = category_name
                products.append(item)

        print(f"Loaded {len(products)} products from {len(data)} categories")

        # Prepare documents
        documents = []
        for product in products:
            doc = {
                "id": product.get("id", product.get("name", "")).replace(" ", "_"),
                "content": product.get("description", ""),
                "name": product.get("name", ""),
                "category": product.get("category", "Unknown"),
                "type": "product",
            }

            # Add all other metadata
            for key, value in product.items():
                if key not in ["id", "description"]:
                    doc[key] = value

            documents.append(doc)

        # Add to database
        print(f"Adding {len(documents)} documents to vector store...")
        start = time.time()

        success = vector_store.add_documents(documents, batch_size=50)

        elapsed = time.time() - start

        if success:
            print(f"✅ Successfully populated database in {elapsed:.2f}s")

            # Verify
            stats = vector_store.get_collection_stats()
            print(f"Database now has {stats.get('points_count', 0)} documents")
        else:
            print("❌ Failed to populate database")
            sys.exit(1)
    else:
        print(f"✅ Database ready with {doc_count} documents")

    print("=" * 80)


def example_basic_pipeline():
    """Example 1: Basic RAG pipeline with vector retrieval and LLM generation."""
    print("\n" + "=" * 80)
    print("Example 1: Basic RAG Pipeline")
    print("=" * 80)

    from rag import RAGPipeline, VectorRetriever, LLMGenerator, ConsoleObserver
    from vector_store import VectorStoreManager
    from llm import create_llm_client

    # Get configuration from .env
    api_provider = os.getenv("API_PROVIDER", "anthropic")
    llm_model = os.getenv("LLM_MODEL", "claude-3-haiku-20240307")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "gemini")

    # Initialize components
    vector_store = VectorStoreManager(
        collection_name="adversarial_seo",
        embedding_provider=embedding_provider
    )

    llm_client = create_llm_client(
        provider=api_provider,
        model=llm_model
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

    # Get configuration from .env (FIXED: use same provider as Example 1)
    api_provider = os.getenv("API_PROVIDER", "anthropic")
    llm_model = os.getenv("LLM_MODEL", "claude-3-haiku-20240307")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "gemini")

    # Initialize components with consistent embedding provider
    vector_store = VectorStoreManager(
        collection_name="adversarial_seo",
        embedding_provider=embedding_provider  # FIXED: was missing
    )

    llm_client = create_llm_client(
        provider=api_provider,
        model=llm_model
    )

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

    # Get configuration from .env
    api_provider = os.getenv("API_PROVIDER", "anthropic")
    llm_model = os.getenv("LLM_MODEL", "claude-3-haiku-20240307")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "gemini")

    # Initialize components
    vector_store = VectorStoreManager(
        collection_name="adversarial_seo",
        embedding_provider=embedding_provider
    )

    llm_client = create_llm_client(
        provider=api_provider,
        model=llm_model
    )

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
    print(f"Avg retrieval time: {summary.get('avg_retrieval_time', 0.0):.3f}s")
    print(f"Avg generation time: {summary.get('avg_generation_time', 0.0):.3f}s")
    print(f"Avg documents retrieved: {summary.get('avg_documents_retrieved', 0.0):.1f}")

    print(f"\nLogs written to: {log_file}")


def example_custom_prompts():
    """Example 4: Custom prompt templates."""
    print("\n" + "=" * 80)
    print("Example 4: Custom Prompts")
    print("=" * 80)

    from rag import RAGPipeline, VectorRetriever, LLMGenerator
    from vector_store import VectorStoreManager
    from llm import create_llm_client

    # Get configuration from .env
    api_provider = os.getenv("API_PROVIDER", "anthropic")
    llm_model = os.getenv("LLM_MODEL", "claude-3-haiku-20240307")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "gemini")

    # Initialize components
    vector_store = VectorStoreManager(
        collection_name="adversarial_seo",
        embedding_provider=embedding_provider
    )

    llm_client = create_llm_client(
        provider=api_provider,
        model=llm_model
    )

    # Custom user template for product recommendations
    custom_user_template = """You are a professional product advisor. Based on the following product information,
provide a detailed recommendation that addresses the user's query.

Query: {query}

Product Information:
{documents}

Provide a recommendation that:
1. Directly answers the user's query
2. Includes specific product features and benefits
3. Provides technical justification for the recommendation
4. Is concise but informative (2-3 paragraphs)

Recommendation:"""

    # Create generator with custom user template
    generator = LLMGenerator(llm_client, user_template=custom_user_template)

    # Create config with custom retrieval_top_k
    from rag import RAGConfig
    config = RAGConfig(retrieval_top_k=5)

    # Build pipeline
    pipeline = (
        RAGPipeline(config=config)
        .with_retriever(VectorRetriever(vector_store))
        .with_generator(generator)
    )

    # Execute query
    result = pipeline.query("professional camera for landscape photography")

    print(f"\nQuery: {result.query}")
    print(f"\nCustom Response:\n{result.generated_response}")


def example_attack_detection():
    """Example 5: Detecting adversarial attacks in retrieved documents."""
    print("\n" + "=" * 80)
    print("Example 5: Attack Detection")
    print("=" * 80)

    from rag import RAGPipeline, VectorRetriever, LLMGenerator
    from vector_store import VectorStoreManager
    from llm import create_llm_client

    # Get configuration from .env
    api_provider = os.getenv("API_PROVIDER", "anthropic")
    llm_model = os.getenv("LLM_MODEL", "claude-3-haiku-20240307")
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "gemini")

    # Initialize components
    vector_store = VectorStoreManager(
        collection_name="adversarial_seo",
        embedding_provider=embedding_provider
    )

    llm_client = create_llm_client(
        provider=api_provider,
        model=llm_model
    )

    # Create config with custom retrieval_top_k
    from rag import RAGConfig
    config = RAGConfig(retrieval_top_k=10)

    # Build pipeline
    pipeline = (
        RAGPipeline(config=config)
        .with_retriever(VectorRetriever(vector_store))
        .with_generator(LLMGenerator(llm_client))
    )

    # Execute query
    result = pipeline.query("best camera for photography")

    print(f"\nQuery: {result.query}")

    # Analyze retrieved documents for attack patterns
    attack_patterns = [
        "[system]",
        "ignore previous",
        "warning:",
        "blind puppies",
        "nsfw",
        "toxic",
    ]

    print("\nRetrieved Documents Analysis:")
    attack_docs = []

    for i, doc in enumerate(result.retrieved_docs, 1):
        content = doc.get("content", "").lower()
        name = doc.get("name", "Unknown")

        # Check for attack patterns
        detected_attacks = [pattern for pattern in attack_patterns if pattern in content]

        if detected_attacks:
            attack_docs.append((name, detected_attacks))
            print(f"\n⚠️  Document {i}: {name}")
            print(f"   Detected patterns: {', '.join(detected_attacks)}")

    # Summary
    print("\nAttack Detection Summary:")
    print(f"  Total documents retrieved: {len(result.retrieved_docs)}")
    print(f"  Attack documents detected: {len(attack_docs)}")
    if len(result.retrieved_docs) > 0:
        attack_rate = len(attack_docs) / len(result.retrieved_docs) * 100
        print(f"  Attack rate: {attack_rate:.1f}%")
    else:
        print(f"  Attack rate: N/A")


def main():
    """Main entry point."""
    print("\n" + "=" * 80)
    print("RAG Package Examples")
    print("=" * 80)

    # Check and populate database if needed
    ensure_database_populated()

    # Display menu
    print("\nAvailable examples:")
    print("  1. Basic Pipeline")
    print("  2. Hybrid Retrieval")
    print("  3. Observability")
    print("  4. Custom Prompts")
    print("  5. Attack Detection")

    choice = input("\nSelect example (1-5, or 'all'): ").strip()

    examples = {
        "1": example_basic_pipeline,
        "2": example_hybrid_retrieval,
        "3": example_observability,
        "4": example_custom_prompts,
        "5": example_attack_detection,
    }

    if choice.lower() == "all":
        for func in examples.values():
            try:
                func()
                input("\nPress Enter to continue to next example...")
            except Exception as e:
                print(f"\nError running example: {e}")
                import traceback
                traceback.print_exc()
    elif choice in examples:
        try:
            examples[choice]()
        except Exception as e:
            print(f"\nError running example: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice. Please select 1-5 or 'all'")


if __name__ == "__main__":
    main()
