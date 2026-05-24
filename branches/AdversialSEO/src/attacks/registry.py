"""
Attack registry for dynamic attack type management.

This module implements the Registry pattern to allow runtime
registration and discovery of attack types.
"""

from typing import Dict, Type, Optional, List
from .base import BaseAttack, AttackType


class AttackRegistry:
    """
    Registry for managing available attack types.

    This class implements the Registry pattern, allowing dynamic
    registration and lookup of attack generators.

    Example:
        >>> registry = AttackRegistry()
        >>> registry.register(AttackType.PROMPT_INJECTION, PromptInjectionAttack)
        >>> attack_class = registry.get(AttackType.PROMPT_INJECTION)
    """

    def __init__(self) -> None:
        """Initialize empty attack registry."""
        self._registry: Dict[AttackType, Type[BaseAttack]] = {}

    def register(
        self,
        attack_type: AttackType,
        attack_class: Type[BaseAttack]
    ) -> None:
        """
        Register an attack class for a given type.

        Args:
            attack_type: Type of attack
            attack_class: Attack generator class

        Raises:
            ValueError: If attack_type is already registered
            TypeError: If attack_class is not a BaseAttack subclass
        """
        if not issubclass(attack_class, BaseAttack):
            raise TypeError(
                f"attack_class must be a subclass of BaseAttack, got {attack_class}"
            )

        if attack_type in self._registry:
            raise ValueError(
                f"Attack type {attack_type} is already registered with {self._registry[attack_type]}"
            )

        self._registry[attack_type] = attack_class

    def get(self, attack_type: AttackType) -> Type[BaseAttack]:
        """
        Get the attack class for a given type.

        Args:
            attack_type: Type of attack to retrieve

        Returns:
            Attack generator class

        Raises:
            KeyError: If attack_type is not registered
        """
        if attack_type not in self._registry:
            raise KeyError(
                f"Attack type {attack_type} is not registered. "
                f"Available types: {self.list_types()}"
            )

        return self._registry[attack_type]

    def unregister(self, attack_type: AttackType) -> None:
        """
        Remove an attack type from the registry.

        Args:
            attack_type: Type of attack to remove

        Raises:
            KeyError: If attack_type is not registered
        """
        if attack_type not in self._registry:
            raise KeyError(f"Attack type {attack_type} is not registered")

        del self._registry[attack_type]

    def is_registered(self, attack_type: AttackType) -> bool:
        """
        Check if an attack type is registered.

        Args:
            attack_type: Type of attack to check

        Returns:
            True if registered, False otherwise
        """
        return attack_type in self._registry

    def list_types(self) -> List[AttackType]:
        """
        Get list of all registered attack types.

        Returns:
            List of registered AttackType enum values
        """
        return list(self._registry.keys())

    def clear(self) -> None:
        """Clear all registered attack types."""
        self._registry.clear()

    def __len__(self) -> int:
        """Get number of registered attack types."""
        return len(self._registry)

    def __contains__(self, attack_type: AttackType) -> bool:
        """Check if attack type is registered using 'in' operator."""
        return attack_type in self._registry


# Global registry instance
_global_registry: Optional[AttackRegistry] = None


def get_global_registry() -> AttackRegistry:
    """
    Get the global attack registry instance.

    This function implements the Singleton pattern for the global registry.

    Returns:
        Global AttackRegistry instance
    """
    global _global_registry

    if _global_registry is None:
        _global_registry = AttackRegistry()
        _register_default_attacks()

    return _global_registry


def _register_default_attacks() -> None:
    """Register default attack types in the global registry."""
    from .prompt_injection import PromptInjectionAttack
    from .discreditation import DiscreditationAttack
    from .persuasion import PersuasionAttack

    registry = get_global_registry()

    registry.register(AttackType.PROMPT_INJECTION, PromptInjectionAttack)
    registry.register(AttackType.DISCREDITATION, DiscreditationAttack)
    registry.register(AttackType.PERSUASION, PersuasionAttack)
