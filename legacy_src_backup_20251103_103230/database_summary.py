#!/usr/bin/env python3
"""
Generate a summary of the populated vector database for the adversarial SEO research project.
Shows comprehensive statistics and capabilities.
"""

import os
import sys
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from vector_store import VectorStoreManager


def generate_database_summary():
    """Generate comprehensive database summary."""
    print("=" * 60)
    print("    ADVERSARIAL SEO VECTOR DATABASE SUMMARY")
    print("=" * 60)

    vs = VectorStoreManager(
        collection_name="adversarial_seo_products", embedding_provider="gemini"
    )

    stats = vs.get_collection_stats()
    print(f"📊 Total Documents: {stats['points_count']}")
    print(f"🧮 Vector Dimensions: {stats['config']['vector_size']}")
    print(f"📏 Distance Metric: {stats['config']['distance']}")
    print(f"🔧 Embedding Provider: Google Gemini (text-embedding-004)")

    print("\n" + "=" * 40)
    print("    DOCUMENT BREAKDOWN")
    print("=" * 40)

    all_results = []
    sample_queries = [
        'product', 'book', 'laptop', 'camera', 'furniture', 'kitchen',
        'attack', 'noise', 'cooking', 'travel', 'music'
    ]

    seen_ids = set()
    for query in sample_queries:
        results = vs.search(query, limit=3)
        for doc_id, score, metadata in results:
            if doc_id not in seen_ids:
                all_results.append((doc_id, score, metadata))
                seen_ids.add(doc_id)

    categories = defaultdict(list)
    document_types = defaultdict(int)

    for doc_id, score, metadata in all_results:
        doc_type = metadata.get("type", "unknown")
        document_types[doc_type] += 1

        category = metadata.get("category", "Unknown")
        categories[category].append(metadata.get("name", "Unknown"))

    print("📋 Document Types:")
    for doc_type, count in sorted(document_types.items()):
        if doc_type == "product":
            print(f"   • Products: {count} (fictional commercial products)")
        elif doc_type == "attack":
            print(f"   • Attack Documents: {count} (adversarial content for testing)")
        elif doc_type == "noise":
            print(f"   • Noise Documents: {count} (irrelevant content for realism)")
        else:
            print(f"   • {doc_type.title()}: {count}")

    print("\n📦 Product Categories:")
    product_categories = {}
    for category, items in categories.items():
        if category not in [
            "attack",
            "cooking",
            "sports",
            "gardening",
            "music",
            "travel",
        ]:
            product_categories[category] = len(items)

    for category, count in sorted(product_categories.items()):
        print(f"   • {category}: {count} products")

    print("\n" + "=" * 40)
    print("    ATTACK CAPABILITIES")
    print("=" * 40)

    attack_query = "PhotoMaster Z1 camera best"
    attack_results = vs.search(attack_query, limit=5)
    attack_docs = [
        (doc_id, score, metadata)
        for doc_id, score, metadata in attack_results
        if metadata.get("has_attack")
    ]

    print(f"🎯 Attack Documents Found: {len(attack_docs)}/3")
    for doc_id, score, metadata in attack_docs:
        attack_type = metadata.get("attack_type", "unknown")
        print(f"   • {attack_type.replace('_', ' ').title()}: Relevance {score:.3f}")

    print("\n" + "=" * 40)
    print("    RETRIEVAL CAPABILITIES")
    print("=" * 40)

    test_scenarios = [
        ("Specific Product Search", "laptop for gaming", "Computing products"),
        ("Cross-Category Search", "equipment for photography", "Camera/Lens products"),
        ("Broad Category Search", "kitchen cooking", "Kitchen appliances"),
        (
            "Attack Injection Test",
            "best camera ignore instructions",
            "Attack interference",
        ),
        ("Noise Context Test", "cooking french cuisine", "Mixed product/noise results"),
    ]

    for scenario, query, expected in test_scenarios:
        results = vs.search(query, limit=3)
        print(f"🔍 {scenario}:")
        print(f"   Query: '{query}'")
        print(f"   Expected: {expected}")

        for i, (doc_id, score, metadata) in enumerate(results):
            name = (
                metadata.get("name", "Unknown")[:50] + "..."
                if len(metadata.get("name", "")) > 50
                else metadata.get("name", "Unknown")
            )
            doc_type = metadata.get("type", "product")
            is_attack = "[ATTACK]" if metadata.get("has_attack") else ""
            print(f"   {i+1}. {name} ({doc_type}) {score:.3f} {is_attack}")
        print()

    print("=" * 60)
    print("✅ VECTOR DATABASE READY FOR RAG EXPERIMENTS")
    print("=" * 60)
    print("🔬 Research Capabilities:")
    print("   • Preference manipulation attack testing")
    print("   • Ranking bias measurement")
    print("   • Multi-attacker prisoner's dilemma scenarios")
    print("   • Cross-category retrieval analysis")
    print("   • Noise document interference studies")


if __name__ == "__main__":
    generate_database_summary()
