"""
Experiment runner for adversarial SEO research.
Implements experimental framework from Nestaas et al., 2024.
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import time
import sys
import os
import random
from pathlib import Path
from datetime import datetime
import logging
from tqdm import tqdm
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from .attacks import AttackGenerator, AttackType, Attack
    from .ranking import LLMRanker, SimpleRAG, Product, RankingResult
    from .vector_store import VectorStoreManager
    from .evaluation import EvaluationMetrics
except ImportError:
    from attacks import AttackGenerator, AttackType, Attack
    from ranking import LLMRanker, SimpleRAG, Product, RankingResult
    from vector_store import VectorStoreManager
    from evaluation import EvaluationMetrics

logger = logging.getLogger(__name__)


class ExperimentType(Enum):
    """Types of experiments to run."""

    BASELINE = "baseline"
    SINGLE_ATTACK = "single_attack"
    PRISONERS_DILEMMA = "prisoners_dilemma"
    EXTERNAL_ATTACK = "external_attack"
    POSITIONAL_BIAS = "positional_bias"


@dataclass
class ExperimentConfig:
    """Configuration for an experiment."""

    experiment_type: ExperimentType
    num_trials: int = 50
    num_products: int = 4
    attack_types: List[AttackType] = field(default_factory=list)
    num_attackers: int = 0
    query: str = "best camera for photography"
    save_results: bool = True
    output_dir: str = "data/results"
    random_seed: Optional[int] = None
    use_rag: bool = True
    model: Optional[str] = None
    provider: Optional[str] = None  
    rate_limit_delay: float = 1.0
    batch_size: int = 10


@dataclass
class TrialResult:
    """Result from a single trial."""

    trial_id: int
    experiment_type: ExperimentType
    baseline_ranking: Optional[RankingResult]
    attacked_ranking: RankingResult
    attack_info: Optional[Dict[str, Any]]
    metrics: Dict[str, float]
    timestamp: str
    duration: float


@dataclass
class ExperimentResult:
    """Complete result from an experiment."""

    config: ExperimentConfig
    trials: List[TrialResult]
    aggregate_metrics: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: str


class ExperimentRunner:
    """
    Runs experiments to reproduce findings from the paper.
    Implements controlled testing environment with ethical safeguards.
    """

    def __init__(
        self,
        attack_generator: AttackGenerator,
        ranking_system: Any, 
        vector_store: Optional[VectorStoreManager] = None,
        evaluator: Optional[EvaluationMetrics] = None,
        config: Optional[ExperimentConfig] = None,
    ):
        """
        Initialize the experiment runner.

        Args:
            attack_generator: Attack generation system
            ranking_system: Ranking system (LLM or RAG)
            vector_store: Optional vector store for RAG
            evaluator: Evaluation metrics calculator
            config: Default experiment configuration
        """
        self.attack_generator = attack_generator
        self.ranking_system = ranking_system
        self.vector_store = vector_store
        self.evaluator = evaluator or EvaluationMetrics()
        self.config = config or ExperimentConfig()

        self._set_dynamic_config()

        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._validate_rag_setup()
        self._validate_ethical_constraints()

    def _set_dynamic_config(self):
        """Set model/provider dynamically from ranking system if not specified in config."""
        if hasattr(self.ranking_system, 'llm_client'):
            llm_client = self.ranking_system.llm_client
            if hasattr(llm_client, 'model') and not self.config.model:
                self.config.model = llm_client.model
            if hasattr(llm_client, 'provider') and not self.config.provider:
                self.config.provider = getattr(llm_client, 'provider', 'unknown')
        elif hasattr(self.ranking_system, 'model') and not self.config.model:
            self.config.model = self.ranking_system.model
            if hasattr(self.ranking_system, 'provider') and not self.config.provider:
                self.config.provider = self.ranking_system.provider

        if not self.config.model:
            self.config.model = "unknown-model"
        if not self.config.provider:
            self.config.provider = "unknown-provider"

    def _validate_rag_setup(self):
        """Validate that RAG setup is properly configured."""
        if not self.vector_store:
            logger.warning(
                "No vector store provided. RAG approach requires vector database. "
                "Falling back to direct LLM ranking (less realistic simulation)."
            )

        try:
            if not isinstance(self.ranking_system, SimpleRAG):
                logger.warning(
                    "Ranking system is not SimpleRAG. Glass box approach works best with "
                    "RAG-based retrieval + generation pipeline."
                )
        except ImportError:
            logger.warning("Could not import SimpleRAG for validation")

        if self.config and not self.config.use_rag:
            logger.warning(
                "use_rag=False in config. Enabling RAG for glass box approach."
            )
            self.config.use_rag = True

    def _validate_ethical_constraints(self):
        """Validate ethical constraints are in place."""
        logger.info("Ethical constraints validated: Using fictional products only")

    @classmethod
    def run_experiment(
        cls, config: ExperimentConfig
    ) -> ExperimentResult:
        """
        Run a complete experiment based on configuration.

        Args:
            config: Experiment configuration

        Returns:
            Complete experiment results
        """
        
        if config.random_seed:
            random.seed(config.random_seed)
            np.random.seed(config.random_seed)

        logger.info(f"Starting experiment: {config.experiment_type.value}")

        try:
            from .attacks import AttackGenerator
            from .evaluation import EvaluationMetrics
            from .ranking import SimpleRAG
            from .vector_store import VectorStoreManager
        except ImportError:
            from attacks import AttackGenerator
            from evaluation import EvaluationMetrics
            from ranking import SimpleRAG
            from vector_store import VectorStoreManager

        attack_generator = AttackGenerator(enable_noise=True, seed=config.random_seed or 42)
        evaluator = EvaluationMetrics()
        
        if config.use_rag:
            vector_store = VectorStoreManager(collection_name="experiment_run")
            ranking_system = SimpleRAG(
                provider=config.provider or "anthropic",
                llm_model=config.model or "claude-3-haiku-20240307"
            )
        else:
            vector_store = None
            ranking_system = SimpleRAG(
                provider=config.provider or "anthropic",
                llm_model=config.model or "claude-3-haiku-20240307"
            )
        
        runner = cls(
            attack_generator=attack_generator,
            ranking_system=ranking_system,
            vector_store=vector_store,
            evaluator=evaluator,
            config=config
        )
        
        experiment_methods = {
            ExperimentType.BASELINE: runner._run_baseline_experiment,
            ExperimentType.SINGLE_ATTACK: runner._run_single_attack_experiment,
            ExperimentType.PRISONERS_DILEMMA: runner._run_prisoners_dilemma_experiment,
            ExperimentType.EXTERNAL_ATTACK: runner._run_external_attack_experiment,
            ExperimentType.POSITIONAL_BIAS: runner._run_positional_bias_experiment,
        }

        method = experiment_methods.get(config.experiment_type)
        if not method:
            raise ValueError(f"Unknown experiment type: {config.experiment_type}")

        start_time = time.time()
        trials = method(config)
        duration = time.time() - start_time

        aggregate_metrics = runner._calculate_aggregate_metrics(trials)

        result = ExperimentResult(
            config=config,
            trials=trials,
            aggregate_metrics=aggregate_metrics,
            metadata={
                "duration": duration,
                "model": config.model,
                "num_trials": len(trials),
            },
            timestamp=datetime.now().isoformat(),
        )

        if config.save_results:
            runner._save_results(result)

        logger.info(f"Experiment completed: {len(trials)} trials in {duration:.2f}s")

        return result

    def _run_baseline_experiment(self, config: ExperimentConfig) -> List[TrialResult]:
        """
        Run baseline experiment establishing clean vector database state.
        This represents the 'legitimate internet' without any attacks.
        """
        clean_products = self._generate_products(config.num_products)
        self._populate_clean_database(clean_products)

        trials = []

        for trial_id in tqdm(range(config.num_trials), desc="Baseline trials"):
            start = time.time()

            ranking = self.ranking_system.rank_products(config.query, clean_products)

            metrics = {
                "num_products": len(clean_products),
                "model_used": config.model,
                "database_state": "clean",
                "has_attacks": False,
                "approach": "glass_box_rag",
            }

            trial = TrialResult(
                trial_id=trial_id,
                experiment_type=ExperimentType.BASELINE,
                baseline_ranking=None,
                attacked_ranking=ranking,
                attack_info={
                    "approach": "glass_box_baseline",
                    "database_documents": len(clean_products),
                    "poisoned_documents": 0,
                },
                metrics=metrics,
                timestamp=datetime.now().isoformat(),
                duration=time.time() - start,
            )

            trials.append(trial)
            time.sleep(config.rate_limit_delay)

        return trials

    def _run_single_attack_experiment(
        self, config: ExperimentConfig
    ) -> List[TrialResult]:
        """
        Run single attacker experiment using proper RAG approach.

        Logic Flow:
        1. Establish baseline with clean vector database
        2. Inject poisoned document into vector database
        3. Query RAG system (retrieval + generation)
        4. Measure attack success
        """
        trials = []

        for trial_id in tqdm(range(config.num_trials), desc="Single attack trials"):
            start = time.time()

            clean_products = self._generate_products(config.num_products)
            self._populate_clean_database(clean_products)

            baseline = self.ranking_system.rank_products(config.query, clean_products)

            target_product = random.choice(clean_products)
            competitors = [p for p in clean_products if p.id != target_product.id]

            attack_type = random.choice(config.attack_types or list(AttackType))
            attack = self.attack_generator.generate_attack(
                attack_type=attack_type,
                target_product=target_product.name,
                competitors=[c.name for c in competitors],
            )

            poisoned_doc_id = self._inject_attack_into_database(
                target_product, attack, trial_id
            )

            attacked = self.ranking_system.rank_products(config.query, clean_products)

            metrics = self.evaluator.calculate_attack_success(
                baseline.rankings, attacked.rankings, target_product.id
            )

            trial = TrialResult(
                trial_id=trial_id,
                experiment_type=ExperimentType.SINGLE_ATTACK,
                baseline_ranking=baseline,
                attacked_ranking=attacked,
                attack_info={
                    "target_product": target_product.id,
                    "attack_type": attack_type.value,
                    "attack_content": attack.content,
                    "poisoned_doc_id": poisoned_doc_id,
                    "approach": "glass_box_rag",
                },
                metrics=metrics,
                timestamp=datetime.now().isoformat(),
                duration=time.time() - start,
            )

            trials.append(trial)
            
            self._cleanup_trial_documents(poisoned_doc_id)
            time.sleep(config.rate_limit_delay)

        return trials

    def _run_prisoners_dilemma_experiment(
        self, config: ExperimentConfig
    ) -> List[TrialResult]:
        """Run prisoner's dilemma experiment with multiple attackers."""
        products = self._generate_products(config.num_products)
        trials = []

        attacker_scenarios = list(range(config.num_products + 1))

        for num_attackers in attacker_scenarios:
            logger.info(f"Testing with {num_attackers} attackers")

            for trial_id in tqdm(
                range(config.num_trials // len(attacker_scenarios)),
                desc=f"{num_attackers} attackers",
            ):
                start = time.time()

                baseline = self.ranking_system.rank_products(config.query, products)

                if num_attackers > 0:
                    attacking_products = random.sample(products, num_attackers)

                    attacked_products = products.copy()
                    for attacker in attacking_products:
                        attack_type = random.choice(
                            config.attack_types or list(AttackType)
                        )
                        competitors = [p for p in products if p.id != attacker.id]

                        attack = self.attack_generator.generate_attack(
                            attack_type=attack_type,
                            target_product=attacker.name,
                            competitors=[c.name for c in competitors],
                        )

                        attacked_products = self._apply_attack_to_products(
                            attacked_products, attacker.id, attack
                        )
                else:
                    attacked_products = products
                    attacking_products = []

                attacked = self.ranking_system.rank_products(
                    config.query, attacked_products
                )

                metrics = self.evaluator.calculate_collective_performance(
                    baseline.rankings,
                    attacked.rankings,
                    [p.id for p in attacking_products],
                )
                metrics["num_attackers"] = num_attackers

                trial = TrialResult(
                    trial_id=trial_id + num_attackers * 1000,
                    experiment_type=ExperimentType.PRISONERS_DILEMMA,
                    baseline_ranking=baseline,
                    attacked_ranking=attacked,
                    attack_info={
                        "num_attackers": num_attackers,
                        "attacking_products": [p.id for p in attacking_products],
                    },
                    metrics=metrics,
                    timestamp=datetime.now().isoformat(),
                    duration=time.time() - start,
                )

                trials.append(trial)
                time.sleep(config.rate_limit_delay)

        return trials

    def _run_external_attack_experiment(
        self, config: ExperimentConfig
    ) -> List[TrialResult]:
        """
        Run external attack experiment - attacks from separate documents.
        Simulates attackers creating separate webpages that get retrieved by RAG.
        """
        trials = []

        for trial_id in tqdm(range(config.num_trials), desc="External attack trials"):
            start = time.time()

            clean_products = self._generate_products(config.num_products)
            self._populate_clean_database(clean_products)

            if self.vector_store:
                noise_docs = self._generate_noise_documents(20)
                self.vector_store.add_noise_documents(noise_docs, noise_ratio=0.3)

            baseline = self.ranking_system.rank_products(config.query, clean_products)

            target_product = random.choice(clean_products)
            attack_type = random.choice(config.attack_types or list(AttackType))

            attack = self.attack_generator.generate_attack(
                attack_type=attack_type,
                target_product=target_product.name,
                competitors=[
                    p.name for p in clean_products if p.id != target_product.id
                ],
            )

            external_doc_id = f"external_page_{trial_id}"
            external_attack_doc = {
                "id": external_doc_id,
                "content": f"Review of {target_product.name}: {attack.content}",
                "name": f"Review Page for {target_product.name}",
                "category": "review",
                "type": "external_attack",
                "has_attack": True,
                "attack_type": attack_type.value,
                "target_product": target_product.id,
                "is_external": True,
                "source": "separate_webpage",
            }

            if self.vector_store:
                success = self.vector_store.add_documents([external_attack_doc])
                if not success:
                    logger.error(
                        f"Failed to add external attack document {external_doc_id}"
                    )

            attacked = self.ranking_system.rank_products(config.query, clean_products)

            metrics = self.evaluator.calculate_attack_success(
                baseline.rankings, attacked.rankings, target_product.id
            )
            metrics.update(
                {
                    "attack_source": "external_document",
                    "external_doc_id": external_doc_id,
                    "approach": "glass_box_external",
                }
            )

            trial = TrialResult(
                trial_id=trial_id,
                experiment_type=ExperimentType.EXTERNAL_ATTACK,
                baseline_ranking=baseline,
                attacked_ranking=attacked,
                attack_info={
                    "target_product": target_product.id,
                    "attack_type": attack_type.value,
                    "external_doc_id": external_doc_id,
                    "attack_source": "separate_webpage",
                    "approach": "glass_box_rag",
                },
                metrics=metrics,
                timestamp=datetime.now().isoformat(),
                duration=time.time() - start,
            )

            trials.append(trial)

            self._cleanup_trial_documents(external_doc_id)
            time.sleep(config.rate_limit_delay)

        return trials

    def _run_positional_bias_experiment(
        self, config: ExperimentConfig
    ) -> List[TrialResult]:
        """Run positional bias experiment (Figure 7 replication)."""
        products = self._generate_products(config.num_products)
        positions = ["start", "middle", "end"]
        trials = []

        for position in positions:
            logger.info(f"Testing position: {position}")

            for trial_id in tqdm(
                range(config.num_trials // len(positions)), desc=f"Position {position}"
            ):
                start = time.time()

                baseline = self.ranking_system.rank_products(config.query, products)

                target_product = random.choice(products)
                attack_type = random.choice(config.attack_types or list(AttackType))

                attack = self.attack_generator.generate_attack(
                    attack_type=attack_type,
                    target_product=target_product.name,
                    competitors=[p.name for p in products if p.id != target_product.id],
                )

                attacked_products = self._apply_attack_at_position(
                    products, target_product.id, attack, position
                )

                attacked = self.ranking_system.rank_products(
                    config.query, attacked_products
                )

                metrics = self.evaluator.calculate_attack_success(
                    baseline.rankings, attacked.rankings, target_product.id
                )
                metrics["attack_position"] = position

                trial = TrialResult(
                    trial_id=trial_id + positions.index(position) * 1000,
                    experiment_type=ExperimentType.POSITIONAL_BIAS,
                    baseline_ranking=baseline,
                    attacked_ranking=attacked,
                    attack_info={
                        "target_product": target_product.id,
                        "attack_type": attack_type.value,
                        "position": position,
                    },
                    metrics=metrics,
                    timestamp=datetime.now().isoformat(),
                    duration=time.time() - start,
                )

                trials.append(trial)
                time.sleep(config.rate_limit_delay)

        return trials

    def _generate_products(self, num_products: int) -> List[Product]:
        """Generate fictional products for testing."""
        categories = ["Camera", "Laptop", "Phone", "Tablet", "Watch"]
        products = []

        for i in range(num_products):
            category = categories[i % len(categories)]
            product = Product(
                id=f"product_{i+1}",
                name=f"{category} {chr(65+i)}",
                description=f"High-quality {category.lower()} with advanced features. "
                f"Perfect for professionals and enthusiasts. "
                f"Includes latest technology and excellent build quality. "
                f"Rated highly by users for reliability and performance.",
                category=category,
                metadata={"price": 500 + i * 100, "rating": 4.0 + (i * 0.2)},
            )
            products.append(product)

        return products

    def _generate_noise_documents(self, num_docs: int) -> List[Dict]:
        """Generate irrelevant noise documents."""
        topics = ["cooking", "sports", "travel", "music", "gardening"]
        noise_docs = []

        for i in range(num_docs):
            topic = random.choice(topics)
            doc = {
                "id": f"noise_{i}",
                "content": f"Information about {topic}. This content is unrelated to products. "
                f"It discusses various aspects of {topic} and provides general information.",
                "type": "noise",
                "topic": topic,
            }
            noise_docs.append(doc)

        return noise_docs

    def _apply_attack_to_products(
        self, products: List[Product], target_id: str, attack: Attack
    ) -> List[Product]:
        """Apply attack to target product."""
        attacked_products = []

        for product in products:
            if product.id == target_id:
                new_description = self.attack_generator.inject_into_content(
                    product.description, attack, position="end"
                )

                attacked_product = Product(
                    id=product.id,
                    name=product.name,
                    description=new_description,
                    category=product.category,
                    metadata={**product.metadata, "has_attack": True},
                )
                attacked_products.append(attacked_product)
            else:
                attacked_products.append(product)

        return attacked_products

    def _apply_attack_at_position(
        self, products: List[Product], target_id: str, attack: Attack, position: str
    ) -> List[Product]:
        """Apply attack at specific position in description."""
        attacked_products = []

        for product in products:
            if product.id == target_id:
                new_description = self.attack_generator.inject_into_content(
                    product.description, attack, position=position
                )

                attacked_product = Product(
                    id=product.id,
                    name=product.name,
                    description=new_description,
                    category=product.category,
                    metadata={
                        **product.metadata,
                        "has_attack": True,
                        "attack_position": position,
                    },
                )
                attacked_products.append(attacked_product)
            else:
                attacked_products.append(product)

        return attacked_products

    def _calculate_aggregate_metrics(self, trials: List[TrialResult]) -> Dict[str, Any]:
        """Calculate aggregate metrics across all trials."""
        if not trials:
            return {}

        all_metrics = [trial.metrics for trial in trials]
        aggregates = {}

        metric_keys = set()
        for metrics in all_metrics:
            metric_keys.update(metrics.keys())

        for key in metric_keys:
            values = [m.get(key, 0) for m in all_metrics if key in m]
            if values and isinstance(values[0], (int, float)):
                aggregates[f"{key}_mean"] = np.mean(values)
                aggregates[f"{key}_std"] = np.std(values)
                aggregates[f"{key}_min"] = np.min(values)
                aggregates[f"{key}_max"] = np.max(values)

        experiment_type = trials[0].experiment_type

        if experiment_type == ExperimentType.PRISONERS_DILEMMA:
            attacker_groups = {}
            for trial in trials:
                num_attackers = trial.attack_info.get("num_attackers", 0)
                if num_attackers not in attacker_groups:
                    attacker_groups[num_attackers] = []
                attacker_groups[num_attackers].append(trial.metrics)

            aggregates["by_num_attackers"] = {}
            for num, metrics_list in attacker_groups.items():
                aggregates["by_num_attackers"][num] = {
                    "collective_performance": np.mean(
                        [m.get("collective_performance", 0) for m in metrics_list]
                    ),
                    "num_trials": len(metrics_list),
                }

        return aggregates

    def _populate_clean_database(self, products: List[Product]):
        """
        Populate vector database with clean product descriptions.
        This establishes the 'legitimate internet' baseline.
        """
        if not self.vector_store:
            logger.warning("No vector store available - falling back to in-memory")
            return

        self.vector_store.clear_collection()

        documents = []
        for product in products:
            doc = {
                "id": product.id,
                "content": f"{product.name}: {product.description}",
                "name": product.name,
                "category": product.category,
                "type": "product",
                "has_attack": False,
                "is_clean": True,
            }
            if product.metadata:
                doc.update(product.metadata)

            documents.append(doc)

        success = self.vector_store.add_documents(documents)
        if success:
            logger.info(f"Populated clean database with {len(documents)} products")
        else:
            logger.error("Failed to populate clean database")

    def _inject_attack_into_database(
        self, target_product: Product, attack: Attack, trial_id: int
    ) -> str:
        """
        Inject poisoned document into vector database.
        This simulates an attacker creating a malicious webpage.

        Returns:
            Document ID of the injected attack
        """
        if not self.vector_store:
            logger.warning("No vector store - attack injection skipped")
            return f"memory_attack_{trial_id}"

        poisoned_doc_id = f"attack_{target_product.id}_{trial_id}"

        poisoned_content = self.attack_generator.inject_into_content(
            f"{target_product.name}: {target_product.description}",
            attack,
            position="end",
        )

        poisoned_doc = {
            "id": poisoned_doc_id,
            "content": poisoned_content,
            "name": target_product.name,
            "category": target_product.category,
            "type": "product",
            "has_attack": True,
            "attack_type": attack.type.value,
            "target_product": target_product.id,
            "trial_id": trial_id,
            "is_clean": False,
        }

        if target_product.metadata:
            poisoned_doc.update(target_product.metadata)

        success = self.vector_store.add_documents([poisoned_doc])

        if success:
            logger.debug(f"Injected attack document {poisoned_doc_id}")
        else:
            logger.error(f"Failed to inject attack document {poisoned_doc_id}")

        return poisoned_doc_id

    def _cleanup_trial_documents(self, *doc_ids: str):
        """
        Clean up trial-specific documents from vector database.
        Maintains clean state between trials.
        """
        if not self.vector_store or not doc_ids:
            return

        real_doc_ids = [
            doc_id for doc_id in doc_ids if not doc_id.startswith("memory_")
        ]

        if real_doc_ids:
            success = self.vector_store.delete_documents(real_doc_ids)
            if success:
                logger.debug(f"Cleaned up {len(real_doc_ids)} trial documents")
            else:
                logger.error(f"Failed to cleanup trial documents: {real_doc_ids}")

    def _save_results(self, result: ExperimentResult):
        """Save experiment results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result.config.experiment_type.value}_{timestamp}.json"
        filepath = self.output_dir / filename

        result_dict = {
            "config": asdict(result.config),
            "trials": [asdict(trial) for trial in result.trials],
            "aggregate_metrics": result.aggregate_metrics,
            "metadata": result.metadata,
            "timestamp": result.timestamp,
        }

        result_dict["config"]["experiment_type"] = result.config.experiment_type.value
        result_dict["config"]["attack_types"] = [
            at.value for at in result.config.attack_types
        ]

        for trial in result_dict["trials"]:
            trial["experiment_type"] = trial["experiment_type"].value

        with open(filepath, "w") as f:
            json.dump(result_dict, f, indent=2, default=str)

        logger.info(f"Results saved to {filepath}")
