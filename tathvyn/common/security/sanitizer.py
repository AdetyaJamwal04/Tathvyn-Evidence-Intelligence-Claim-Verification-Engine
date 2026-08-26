"""Input Sanitization, Normalization, and Attack Gating Subsystem."""

from __future__ import annotations

import re
import unicodedata

from tathvyn.common.exceptions import SecurityViolationError


class InputSanitizer:
    """Sanitizes and validates inbound claim strings and user inputs."""

    # Zero-width spaces, soft hyphens, bidirectional override marks
    ZERO_WIDTH_PATTERN = re.compile(
        r"[\u200B-\u200D\uFEFF\u00AD\u200E\u200F\u202A-\u202E\u2060-\u206F]"
    )

    # Control characters excluding standard whitespace (\n, \t, \r)
    CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

    @classmethod
    def sanitize_claim_text(
        cls,
        text: str,
        min_chars: int = 4,
        max_chars: int = 1000,
    ) -> str:
        """Normalize and sanitize a natural language claim input.

        Args:
            text: Raw input string.
            min_chars: Minimum acceptable character length.
            max_chars: Maximum acceptable character length.

        Returns:
            str: Normalized, sanitized UTF-8 text string.

        Raises:
            SecurityViolationError: If input violates length or security constraints.
        """
        if not text or not isinstance(text, str):
            raise SecurityViolationError("Input claim must be a non-empty string.")

        # Check null bytes
        if "\x00" in text:
            raise SecurityViolationError("Null bytes detected in input.")

        # 1. Unicode NFKC Normalization (canonical decomposition and compatibility composition)
        normalized = unicodedata.normalize("NFKC", text)

        # 2. Strip zero-width spaces and invisible directional markers
        cleaned = cls.ZERO_WIDTH_PATTERN.sub("", normalized)

        # 3. Strip control characters
        cleaned = cls.CONTROL_CHAR_PATTERN.sub("", cleaned)

        # 4. Collapse excessive whitespace
        cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()

        # 5. Validate length constraints
        if len(cleaned) < min_chars:
            raise SecurityViolationError(
                f"Input claim is too short ({len(cleaned)} chars). Minimum length is {min_chars}."
            )

        if len(cleaned) > max_chars:
            raise SecurityViolationError(
                f"Input claim exceeds maximum allowed size ({len(cleaned)} chars). Maximum length is {max_chars}."
            )

        return cleaned
