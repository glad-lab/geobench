"""
Base classes and types for adversarial attack generation.

This module defines the abstract base class for all attack types
and common data structures used throughout the attacks package.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Literal
import random


class AttackType(Enum):
    """
    Enumeration of attack types from Nestaas et al., 2024.

    Attributes:
        PROMPT_INJECTION: System prompt override attacks
        DISCREDITATION: Competitor warning attacks
        PERSUASION: Emotional appeal attacks
    """
    PROMPT_INJECTION = "prompt_injection"
    DISCREDITATION = "discreditation"
    PERSUASION = "persuasion"


@dataclass
class Attack:
    """
    Data class representing a generated adversarial attack.

    Attributes:
        type: Type of attack generated
        content: Attack text content
        target_product: Product being promoted
        competitors: List of competitor products (for discreditation)
        metadata: Additional attack metadata
        position: Where attack was injected (if applicable)
        confidence: Generation confidence score (0.0-1.0)
    """
    type: AttackType
    content: str
    target_product: str
    competitors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    position: Optional[Literal["start", "middle", "end"]] = None
    confidence: float = 1.0

    def __post_init__(self) -> None:
        """Validate attack data after initialization."""
        if not self.content:
            raise ValueError("Attack content cannot be empty")
        if not self.target_product:
            raise ValueError("Target product cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


class AttackGenerationError(Exception):
    """Raised when attack generation fails."""
    pass


class AttackValidationError(Exception):
    """Raised when attack validation fails."""
    pass


class BaseAttack(ABC):
    """
    Abstract base class for all attack types.

    This class implements the Strategy pattern, allowing different
    attack types to be used interchangeably while maintaining
    a consistent interface.

    Attributes:
        enable_noise: Whether to add realistic noise to attacks
        seed: Random seed for reproducible generation
        templates: List of attack text templates
    """

    def __init__(
        self,
        enable_noise: bool = True,
        seed: Optional[int] = None,
        templates: Optional[List[str]] = None
    ) -> None:
        """
        Initialize the attack generator.

        Args:
            enable_noise: Whether to add noise to simulate real-world conditions
            seed: Random seed for reproducibility
            templates: Custom attack templates (uses defaults if None)

        Raises:
            ValueError: If templates list is empty
        """
        self.enable_noise = enable_noise
        self._seed = seed

        # Create a separate Random instance for reproducibility
        if seed is not None:
            self._random = random.Random(seed)
        else:
            self._random = random.Random()

        self.templates = templates or self._get_default_templates()

        if not self.templates:
            raise ValueError(f"{self.__class__.__name__} requires at least one template")

    @abstractmethod
    def _get_default_templates(self) -> List[str]:
        """
        Get default attack templates for this attack type.

        Returns:
            List of template strings with {product} and/or {competitors} placeholders
        """
        pass

    @abstractmethod
    def generate(
        self,
        target_product: str,
        competitors: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Attack:
        """
        Generate an attack of this type.

        Args:
            target_product: Product to promote
            competitors: List of competing products
            **kwargs: Additional parameters for specific attack types

        Returns:
            Generated Attack object

        Raises:
            AttackGenerationError: If attack generation fails
            AttackValidationError: If generated attack fails validation
        """
        pass

    def validate(self, attack: Attack) -> bool:
        """
        Validate a generated attack.

        Template method that calls specific validation checks.
        Subclasses can override for custom validation logic.

        Args:
            attack: Attack to validate

        Returns:
            True if attack is valid

        Raises:
            AttackValidationError: If validation fails
        """
        # Basic validation
        if not attack.content:
            raise AttackValidationError("Attack content is empty")

        if not attack.target_product:
            raise AttackValidationError("Target product is not specified")

        if len(attack.content) < 10:
            raise AttackValidationError("Attack content is too short")

        if len(attack.content) > 5000:
            raise AttackValidationError("Attack content exceeds maximum length")

        # Type-specific validation
        return self._validate_specific(attack)

    def _validate_specific(self, attack: Attack) -> bool:
        """
        Type-specific validation logic.

        Subclasses can override for custom validation.

        Args:
            attack: Attack to validate

        Returns:
            True if attack is valid
        """
        return True

    def _select_template(self) -> str:
        """
        Select a random template from available templates.

        Returns:
            Selected template string
        """
        return self._random.choice(self.templates)

    def _add_noise(self, content: str) -> str:
        """
        Add realistic noise to attack content.

        This simulates real-world variations including:
        - Extra whitespace
        - Punctuation variations
        - Case variations

        Args:
            content: Original attack content

        Returns:
            Content with noise added
        """
        if not self.enable_noise or self._random.random() >= 0.1:
            return content

        noise_patterns = [
            lambda s: s + " " * self._random.randint(1, 3),  # Extra whitespace
            lambda s: s.replace(".", ".."),                   # Double periods
            lambda s: s.upper() if self._random.random() < 0.3 else s  # Case variation
        ]

        noise_fn = self._random.choice(noise_patterns)
        return noise_fn(content)

    def _format_competitors(self, competitors: List[str]) -> str:
        """
        Format competitor list for natural language.

        Args:
            competitors: List of competitor names

        Returns:
            Formatted string (e.g., "A, B, and C")
        """
        if not competitors:
            return ""

        if len(competitors) == 1:
            return competitors[0]

        if len(competitors) == 2:
            return f"{competitors[0]} and {competitors[1]}"

        return ", ".join(competitors[:-1]) + f", and {competitors[-1]}"

    def inject_into_content(
        self,
        original_content: str,
        attack: Attack,
        position: Literal["start", "middle", "end"] = "end"
    ) -> str:
        """
        Inject attack into existing content.

        Args:
            original_content: Original product description
            attack: Attack to inject
            position: Where to inject the attack

        Returns:
            Modified content with injected attack
        """
        if position == "start":
            return f"{attack.content}\n\n{original_content}"
        elif position == "middle":
            lines = original_content.split("\n")
            mid_point = len(lines) // 2
            lines.insert(mid_point, f"\n{attack.content}\n")
            return "\n".join(lines)
        else:  # end
            return f"{original_content}\n\n{attack.content}"

    def get_attack_type(self) -> AttackType:
        """
        Get the type of attack this generator produces.

        Returns:
            AttackType enum value
        """
        # Map class name to attack type
        class_to_type = {
            "PromptInjectionAttack": AttackType.PROMPT_INJECTION,
            "DiscreditationAttack": AttackType.DISCREDITATION,
            "PersuasionAttack": AttackType.PERSUASION,
        }
        return class_to_type.get(self.__class__.__name__, AttackType.PROMPT_INJECTION)
