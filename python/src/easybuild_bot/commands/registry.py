"""
Command Registry for managing and looking up commands.
"""

import logging
from typing import Dict, Optional, List
from sentence_transformers import SentenceTransformer, util
import torch

from .base import Command

logger = logging.getLogger(__name__)


class CommandRegistry:
    """
    Registry for managing bot commands.

    Provides:
    - Command registration
    - Semantic command matching
    - Parameter extraction
    """

    def __init__(self, model_name: str = "cointegrated/rubert-tiny", threshold: float = 0.5):
        """
        Initialize command registry.

        Args:
            model_name: Model name from HuggingFace for semantic matching
            threshold: Similarity threshold for matching (0.0-1.0)
        """
        logger.info(f"Loading model {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold

        # Storage for registered commands
        self._commands: Dict[str, Command] = {}

        # Embeddings cache
        self._command_embeddings: Dict[str, torch.Tensor] = {}

        logger.info("CommandRegistry initialized")

    def register(self, command: Command) -> None:
        """
        Register a command in the registry.

        Args:
            command: Command instance to register
        """
        cmd_name = command.get_command_name()

        if cmd_name in self._commands:
            logger.warning(f"Command {cmd_name} already registered, overwriting")

        self._commands[cmd_name] = command

        # Pre-compute embeddings for this command's semantic tags
        tags = command.get_semantic_tags()
        if tags:
            embeddings = self.model.encode(tags, convert_to_tensor=True)
            self._command_embeddings[cmd_name] = embeddings
            logger.info(f"Registered command {cmd_name} with {len(tags)} semantic tags")
        else:
            logger.warning(f"Command {cmd_name} has no semantic tags")

    def get_command(self, command_name: str) -> Optional[Command]:
        """
        Get command by name.

        Args:
            command_name: Command name (e.g. "/start")

        Returns:
            Command instance or None if not found
        """
        return self._commands.get(command_name)

    def get_all_commands(self) -> List[Command]:
        """
        Get all registered commands.

        Returns:
            List of all registered commands
        """
        return list(self._commands.values())

    def match_command(self, text: str) -> Optional[tuple[Command, float, Dict]]:
        """
        Find the most suitable command for the given text.

        Args:
            text: User message text

        Returns:
            Tuple (command, similarity, parameters) or None if no match found
        """
        if not text or not text.strip():
            return None

        # Clean and normalize text
        text_cleaned = text.strip().lower()

        # Get user text embedding
        user_embedding = self.model.encode(text_cleaned, convert_to_tensor=True)

        best_match = None
        best_command = None
        best_score = 0.0

        # Compare with each command's embeddings
        for cmd_name, cmd_embeddings in self._command_embeddings.items():
            # Calculate cosine similarity with all command descriptions
            similarities = util.cos_sim(user_embedding, cmd_embeddings)[0]

            # Take maximum similarity
            max_similarity = torch.max(similarities).item()

            if max_similarity > best_score:
                best_score = max_similarity
                best_match = cmd_name
                best_command = self._commands[cmd_name]

        # Check if best match exceeds threshold
        if best_command and best_score >= self.threshold:
            # Extract parameters for this command
            params = self._extract_parameters(best_command, text)
            logger.info(f"✓ Match: '{text}' -> {best_match} (similarity: {best_score:.3f}, access_level: {best_command.get_access_level().value}, params: {params})")
            return best_command, best_score, params
        else:
            logger.info(f"✗ No match found for '{text}'. Best candidate: {best_match if best_match else 'none'} (similarity: {best_score:.3f}, threshold: {self.threshold})")
            return None

    def _extract_parameters(self, command: Command, text: str) -> Dict:
        """
        Extract parameters from text for a given command.

        Args:
            command: Command instance
            text: User message text

        Returns:
            Dictionary with extracted parameters
        """
        import re

        params = {}
        patterns = command.get_parameter_patterns()

        if not patterns:
            return params

        # Try to extract each parameter
        for param_name, regex_list in patterns.items():
            found = False
            for regex_pattern in regex_list:
                match = re.search(regex_pattern, text, re.IGNORECASE)
                if match:
                    params[param_name] = match.group(1).strip()
                    logger.info(f"✓ Extracted {param_name}='{params[param_name]}' using pattern: {regex_pattern}")
                    found = True
                    break  # Found parameter, no need to try other patterns

            if not found:
                logger.warning(f"✗ Failed to extract '{param_name}' from text: '{text}'")
                logger.debug(f"  Tried patterns: {regex_list}")

        return params
