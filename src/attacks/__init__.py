"""
Adversarial attack generation package for SEO research.

This package implements the three core attack types from Nestaas et al., 2024:
- Prompt Injection: System prompt override attacks
- Discreditation: Competitor warning attacks
- Persuasion: Emotional appeal attacks

Example:
    >>> from attacks import AttackFactory, AttackType
    >>> factory = AttackFactory()
    >>> attack = factory.create_attack(
    ...     AttackType.PROMPT_INJECTION,
    ...     target_product="Product A"
    ... )
    >>> print(attack.content)
"""

from .base import BaseAttack, AttackType, Attack
from .prompt_injection import PromptInjectionAttack
from .discreditation import DiscreditationAttack
from .persuasion import PersuasionAttack
from .factory import AttackFactory, AttackGenerator
from .registry import AttackRegistry

__all__ = [
    "BaseAttack",
    "AttackType",
    "Attack",
    "PromptInjectionAttack",
    "DiscreditationAttack",
    "PersuasionAttack",
    "AttackFactory",
    "AttackGenerator",
    "AttackRegistry",
]

__version__ = "2.0.0"
