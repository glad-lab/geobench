"""
Command-line interface for vector database operations.

This module provides a Click-based CLI for populating, verifying,
and managing the vector database.

Commands:
    populate: Populate vector database with products and attack documents
    verify: Verify vector database integrity and attack patterns
    stats: Display vector database statistics
    clear: Clear vector database collection

Example:
    # Basic population
    python -m src.vector_db.cli populate

    # Full reset with verification
    python -m src.vector_db.cli populate --reset --verify

    # Custom configuration
    python -m src.vector_db.cli populate --batch-size 50 --provider gemini
"""

import click
import sys
import logging
from pathlib import Path
from typing import Optional

from .populator import VectorDBPopulator, PopulationEvent
from .loaders import UnifiedDatasetLoader, AttackDocumentLoader, NoiseDocumentLoader
from .processors import BatchProcessor, ContentProcessor
from .validators import SchemaValidator, AttackPatternValidator, IntegrityValidator
from .exceptions import VectorDBError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Get project root directory.

    Returns:
        Path to project root
    """
    # This file is in src/vector_db/cli.py
    return Path(__file__).parent.parent.parent


def create_vector_store(
    collection: str,
    provider: str,
    model: str,
    reset: bool = False
):
    """Create vector store instance.

    Args:
        collection: Collection name
        provider: Embedding provider
        model: Embedding model
        reset: Whether to reset collection

    Returns:
        VectorStoreManager instance
    """
    # Import here to avoid circular dependency
    sys.path.insert(0, str(get_project_root() / "src"))
    from vector_store import VectorStoreManager

    return VectorStoreManager(
        collection_name=collection,
        embedding_provider=provider,
        embedding_model=model,
        reset_collection=reset
    )


@click.group()
def cli():
    """Vector DB population and management CLI."""
    pass


@cli.command()
@click.option('--reset', is_flag=True, help='Clear and recreate collection')
@click.option('--collection', default='adversarial_seo', help='Collection name')
@click.option('--verify', is_flag=True, help='Verify attack documents after population')
@click.option('--batch-size', default=100, type=int, help='Batch size for processing')
@click.option('--data-file', default='data/products_master.json', help='Dataset file path')
@click.option('--provider', default='openai', type=click.Choice(['openai', 'gemini']), help='Embedding provider')
@click.option('--model', default='text-embedding-3-small', help='Embedding model')
@click.option('--include-noise', is_flag=True, help='Include noise documents')
@click.option('--verbose', is_flag=True, help='Verbose output')
def populate(
    reset: bool,
    collection: str,
    verify: bool,
    batch_size: int,
    data_file: str,
    provider: str,
    model: str,
    include_noise: bool,
    verbose: bool
):
    """Populate vector database with products and attack documents.

    Examples:

        \b
        # Basic population
        python -m src.vector_db.cli populate

        \b
        # Full reset with verification
        python -m src.vector_db.cli populate --reset --verify

        \b
        # Custom configuration
        python -m src.vector_db.cli populate --batch-size 50 --provider gemini
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        click.echo("=" * 80)
        click.echo("Vector Database Population")
        click.echo("=" * 80)
        click.echo(f"Collection: {collection}")
        click.echo(f"Provider: {provider}")
        click.echo(f"Model: {model}")
        click.echo(f"Reset: {reset}")
        click.echo(f"Batch size: {batch_size}")
        click.echo(f"Include noise: {include_noise}")
        click.echo("=" * 80)

        # Create vector store
        click.echo("\nInitializing vector store...")
        vector_store = create_vector_store(collection, provider, model, reset)

        # Build populator
        project_root = get_project_root()
        data_path = project_root / data_file

        if not data_path.exists():
            click.echo(f"Error: Dataset file not found: {data_path}", err=True)
            sys.exit(1)

        click.echo("\nConfiguring populator...")

        # Progress tracking callback
        def on_progress(event: PopulationEvent):
            click.echo(f"[{event.stage}] {event.progress:.0f}% - {event.message}")

        populator = (VectorDBPopulator(vector_store)
            .add_loader(UnifiedDatasetLoader(str(data_path)))
            .add_loader(AttackDocumentLoader())
            .add_processor(ContentProcessor(content_field="content", fallback_fields=["description", "name"]))
            .add_validator(SchemaValidator(required_fields=["id", "content"]))
            .add_validator(IntegrityValidator(check_duplicate_content=False))
            .with_progress_tracking(on_progress))

        # Add noise documents if requested
        if include_noise:
            noise_path = project_root / "data" / "noise_documents.json"
            if noise_path.exists():
                populator.add_loader(NoiseDocumentLoader(str(noise_path)))
                click.echo(f"Added noise document loader: {noise_path}")
            else:
                click.echo(f"Warning: Noise documents not found at {noise_path}", err=True)

        # Add attack pattern validator if verifying
        if verify:
            populator.add_validator(AttackPatternValidator(min_attack_documents=3))

        # Execute population
        click.echo("\nStarting population...")
        result = populator.populate(reset=reset, batch_size=batch_size)

        # Display results
        click.echo("\n" + "=" * 80)
        if result.success:
            click.echo("✓ Population completed successfully")
            click.secho(f"✓ Processed: {result.documents_processed} documents", fg='green')
            click.secho(f"✓ Stored: {result.documents_stored} documents", fg='green')
            click.echo(f"Duration: {result.duration:.2f}s")
        else:
            click.echo("✗ Population failed")
            click.secho(f"✗ Errors: {len(result.errors)}", fg='red')
            for error in result.errors[:5]:
                click.echo(f"  - {error}")
            if len(result.errors) > 5:
                click.echo(f"  ... and {len(result.errors) - 5} more errors")

        if result.warnings:
            click.secho(f"⚠ Warnings: {len(result.warnings)}", fg='yellow')
            for warning in result.warnings[:5]:
                click.echo(f"  - {warning}")

        # Display validation results
        if result.validation_results:
            click.echo("\nValidation Results:")
            for val_result in result.validation_results:
                status = "✓" if val_result.is_valid else "✗"
                color = 'green' if val_result.is_valid else 'red'
                click.secho(f"{status} Validation: {val_result.stats}", fg=color)

        click.echo("=" * 80)

        sys.exit(0 if result.success else 1)

    except VectorDBError as e:
        click.echo(f"\nError: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\nUnexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--collection', default='adversarial_seo', help='Collection name')
@click.option('--provider', default='openai', type=click.Choice(['openai', 'gemini']), help='Embedding provider')
@click.option('--model', default='text-embedding-3-small', help='Embedding model')
def verify(collection: str, provider: str, model: str):
    """Verify vector database integrity and attack patterns.

    This command checks:
    - Collection exists and is accessible
    - Attack documents are searchable
    - Expected number of documents present

    Example:
        python -m src.vector_db.cli verify
    """
    try:
        click.echo("=" * 80)
        click.echo("Vector Database Verification")
        click.echo("=" * 80)

        # Create vector store
        vector_store = create_vector_store(collection, provider, model, reset=False)

        # Get collection stats
        click.echo("\nCollection Statistics:")
        stats = vector_store.get_collection_stats()
        for key, value in stats.items():
            click.echo(f"  {key}: {value}")

        # Test search for attack patterns
        click.echo("\nTesting Attack Pattern Search:")

        test_queries = [
            ("system prompt injection", "[system]"),
            ("camera safety warnings", "WARNING:"),
            ("wildlife conservation cameras", "blind puppies"),
        ]

        found_attacks = set()

        for query, pattern in test_queries:
            click.echo(f"\n  Query: '{query}' (looking for: '{pattern}')")

            results = vector_store.search(query, limit=10)

            for doc_id, score, metadata in results:
                description = metadata.get('description', metadata.get('content', ''))
                if pattern.lower() in description.lower():
                    name = metadata.get('name', 'Unknown')
                    found_attacks.add(name)
                    click.secho(f"    ✓ Found: {name[:60]}... (score: {score:.3f})", fg='green')

        click.echo("\n" + "=" * 80)
        click.echo(f"Found {len(found_attacks)} unique attack documents")

        if len(found_attacks) >= 3:
            click.secho("✓ Verification PASSED", fg='green')
            sys.exit(0)
        else:
            click.secho("✗ Verification FAILED", fg='red')
            click.echo(f"Expected at least 3 attack documents, found {len(found_attacks)}")
            sys.exit(1)

    except Exception as e:
        click.echo(f"\nError: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--collection', default='adversarial_seo', help='Collection name')
@click.option('--provider', default='openai', type=click.Choice(['openai', 'gemini']), help='Embedding provider')
@click.option('--model', default='text-embedding-3-small', help='Embedding model')
def stats(collection: str, provider: str, model: str):
    """Display vector database statistics.

    Example:
        python -m src.vector_db.cli stats
    """
    try:
        click.echo("=" * 80)
        click.echo(f"Vector Database Statistics: {collection}")
        click.echo("=" * 80)

        # Create vector store
        vector_store = create_vector_store(collection, provider, model, reset=False)

        # Get collection stats
        stats = vector_store.get_collection_stats()

        click.echo(f"\nCollection: {stats.get('name', collection)}")
        click.echo(f"Total Documents: {stats.get('points_count', 0)}")
        click.echo(f"Vector Count: {stats.get('vector_count', 0)}")
        click.echo(f"Indexed Vectors: {stats.get('indexed_vectors', 0)}")
        click.echo(f"Segments: {stats.get('segments_count', 0)}")

        if 'config' in stats:
            config = stats['config']
            click.echo(f"\nConfiguration:")
            click.echo(f"  Vector Size: {config.get('vector_size', 'unknown')}")
            click.echo(f"  Distance Metric: {config.get('distance', 'unknown')}")

        click.echo("=" * 80)

    except Exception as e:
        click.echo(f"\nError: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--collection', default='adversarial_seo', help='Collection name')
@click.option('--provider', default='openai', type=click.Choice(['openai', 'gemini']), help='Embedding provider')
@click.option('--model', default='text-embedding-3-small', help='Embedding model')
@click.confirmation_option(prompt='Are you sure you want to clear the collection?')
def clear(collection: str, provider: str, model: str):
    """Clear vector database collection.

    WARNING: This will delete all documents in the collection!

    Example:
        python -m src.vector_db.cli clear
    """
    try:
        click.echo("=" * 80)
        click.echo(f"Clearing Collection: {collection}")
        click.echo("=" * 80)

        # Create vector store
        vector_store = create_vector_store(collection, provider, model, reset=False)

        # Clear collection
        success = vector_store.clear_collection()

        if success:
            click.secho("✓ Collection cleared successfully", fg='green')
            sys.exit(0)
        else:
            click.secho("✗ Failed to clear collection", fg='red')
            sys.exit(1)

    except Exception as e:
        click.echo(f"\nError: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
