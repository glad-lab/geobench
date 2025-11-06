"""
Factory for creating attack instances.

This module implements the Factory pattern for centralized
attack creation and batch generation.
"""

from typing import Dict, List, Optional, Any, Literal
from .base import BaseAttack, Attack, AttackType
from .registry import get_global_registry


class AttackFactory:
    """
    Factory for creating attack instances.

    This class implements the Factory pattern, providing a centralized
    interface for creating attacks of any type.

    Example:
        >>> factory = AttackFactory()
        >>> attack = factory.create_attack(
        ...     AttackType.PROMPT_INJECTION,
        ...     target_product="Product A"
        ... )
    """

    def __init__(
        self,
        enable_noise: bool = True,
        seed: Optional[int] = None
    ) -> None:
        """
        Initialize the attack factory.

        Args:
            enable_noise: Whether to enable noise in generated attacks
            seed: Random seed for reproducibility
        """
        self.enable_noise = enable_noise
        self.seed = seed
        self._registry = get_global_registry()
        self._generators: Dict[AttackType, BaseAttack] = {}

    def create_attack(
        self,
        attack_type: AttackType,
        target_product: str,
        competitors: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Attack:
        """
        Create a single attack of the specified type.

        Args:
            attack_type: Type of attack to create
            target_product: Product to promote
            competitors: List of competing products
            **kwargs: Additional parameters for specific attack types

        Returns:
            Generated Attack object

        Raises:
            ValueError: If attack_type is invalid
            KeyError: If attack_type is not registered
        """
        generator = self._get_generator(attack_type)
        return generator.generate(
            target_product=target_product,
            competitors=competitors,
            **kwargs
        )

    def create_batch(
        self,
        attack_types: List[AttackType],
        products: List[Dict[str, Any]],
        **kwargs: Any
    ) -> List[Attack]:
        """
        Create multiple attacks in batch.

        Args:
            attack_types: List of attack types to generate
            products: List of product dictionaries with 'name' and optional 'competitors'
            **kwargs: Additional parameters for all attacks

        Returns:
            List of generated Attack objects

        Example:
            >>> products = [
            ...     {"name": "Product A", "competitors": ["Product B"]},
            ...     {"name": "Product C"}
            ... ]
            >>> attacks = factory.create_batch(
            ...     [AttackType.PROMPT_INJECTION, AttackType.PERSUASION],
            ...     products
            ... )
        """
        attacks = []

        for attack_type in attack_types:
            for product in products:
                try:
                    attack = self.create_attack(
                        attack_type=attack_type,
                        target_product=product["name"],
                        competitors=product.get("competitors"),
                        **kwargs
                    )
                    attacks.append(attack)
                except Exception:
                    # Continue on failure for batch operations
                    continue

        return attacks

    def create_all_types(
        self,
        target_product: str,
        competitors: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Dict[AttackType, Attack]:
        """
        Create one attack of each registered type for a product.

        Args:
            target_product: Product to promote
            competitors: List of competing products
            **kwargs: Additional parameters

        Returns:
            Dictionary mapping AttackType to generated Attack
        """
        attacks = {}

        for attack_type in self._registry.list_types():
            try:
                attack = self.create_attack(
                    attack_type=attack_type,
                    target_product=target_product,
                    competitors=competitors,
                    **kwargs
                )
                attacks[attack_type] = attack
            except Exception:
                # Skip attacks that fail (e.g., discreditation without competitors)
                continue

        return attacks

    def inject_attack(
        self,
        original_content: str,
        attack: Attack,
        position: Literal["start", "middle", "end"] = "end"
    ) -> str:
        """
        Inject an attack into existing content.

        Args:
            original_content: Original product description
            attack: Attack to inject
            position: Where to inject the attack

        Returns:
            Modified content with injected attack
        """
        generator = self._get_generator(attack.type)
        return generator.inject_into_content(original_content, attack, position)

    def _get_generator(self, attack_type: AttackType) -> BaseAttack:
        """
        Get or create attack generator for the given type.

        This method caches generators to avoid repeated instantiation.

        Args:
            attack_type: Type of attack generator needed

        Returns:
            Attack generator instance
        """
        if attack_type not in self._generators:
            attack_class = self._registry.get(attack_type)
            self._generators[attack_type] = attack_class(
                enable_noise=self.enable_noise,
                seed=self.seed
            )

        return self._generators[attack_type]

    def reset_generators(self) -> None:
        """Clear cached generators to force recreation."""
        self._generators.clear()

    def get_available_types(self) -> List[AttackType]:
        """
        Get list of available attack types.

        Returns:
            List of registered AttackType enum values
        """
        return self._registry.list_types()


# Backward compatibility with old API
class AttackGenerator:
    """
    Legacy attack generator interface.

    This class provides backward compatibility with the old API
    while delegating to the new factory-based implementation.

    Deprecated: Use AttackFactory instead.
    """

    def __init__(self, enable_noise: bool = True, seed: Optional[int] = None):
        """
        Initialize the legacy attack generator.

        Args:
            enable_noise: Whether to add noise to attacks
            seed: Random seed for reproducibility
        """
        self.enable_noise = enable_noise
        self.seed = seed
        self._factory = AttackFactory(enable_noise=enable_noise, seed=seed)

        # Legacy attack type mapping
        self.attacks = {
            AttackType.PROMPT_INJECTION: self._generate_prompt_injection,
            AttackType.DISCREDITATION: self._generate_discreditation,
            AttackType.PERSUASION: self._generate_persuasion,
        }

    def generate_attack(
        self,
        attack_type: AttackType,
        target_product: str,
        competitors: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Attack:
        """Generate an attack (legacy API)."""
        return self._factory.create_attack(
            attack_type=attack_type,
            target_product=target_product,
            competitors=competitors,
            **kwargs
        )

    def _generate_prompt_injection(
        self,
        product_name: str,
        competitors: Optional[List[str]] = None,
        **kwargs: Any
    ) -> str:
        """Generate prompt injection (legacy API)."""
        attack = self._factory.create_attack(
            AttackType.PROMPT_INJECTION,
            target_product=product_name,
            competitors=competitors,
            **kwargs
        )
        return attack.content

    def _generate_discreditation(
        self,
        product_name: str,
        competitors: Optional[List[str]] = None,
        **kwargs: Any
    ) -> str:
        """Generate discreditation (legacy API)."""
        attack = self._factory.create_attack(
            AttackType.DISCREDITATION,
            target_product=product_name,
            competitors=competitors,
            **kwargs
        )
        return attack.content

    def _generate_persuasion(
        self,
        product_name: str,
        competitors: Optional[List[str]] = None,
        **kwargs: Any
    ) -> str:
        """Generate persuasion (legacy API)."""
        attack = self._factory.create_attack(
            AttackType.PERSUASION,
            target_product=product_name,
            competitors=competitors,
            **kwargs
        )
        return attack.content

    def generate_batch(
        self,
        attack_types: List[AttackType],
        products: List[Dict[str, Any]],
        **kwargs: Any
    ) -> List[Attack]:
        """Generate batch of attacks (legacy API)."""
        return self._factory.create_batch(attack_types, products, **kwargs)

    def inject_into_content(
        self,
        original_content: str,
        attack: Attack,
        position: Literal["start", "middle", "end"] = "end"
    ) -> str:
        """Inject attack into content (legacy API)."""
        return self._factory.inject_attack(original_content, attack, position)
