"""
Module for semantic matching of user messages with bot commands
using the ruBert-tiny model from Sberbank.
"""
import logging
from typing import Optional, Tuple
from sentence_transformers import SentenceTransformer, util
import torch

logger = logging.getLogger(__name__)


class CommandMatcher:
    """Class for semantic matching of text with bot commands."""
    
    def __init__(self, model_name: str = "cointegrated/rubert-tiny", threshold: float = 0.5):
        """
        Initialize the model for command matching.
        
        Args:
            model_name: Model name from HuggingFace
            threshold: Similarity threshold for matching (0.0-1.0)
        """
        logger.info(f"Loading model {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold
        
        # Define commands and their descriptions in Russian
        self.commands = {
            "/start": [
                "начать",
                "начать работу",
                "начать работу с ботом",
                "привет",
                "приветствие",
                "старт"
            ],
            "/help": [
                "помощь",
                "помоги",
                "помоги мне",
                "справка",
                "что ты умеешь",
                "как тебя использовать",
                "инструкция"
            ],
            "/build": [
                "сборка",
                "сборки",
                "покажи сборки",
                "выбрать сборку",
                "собрать",
                "билд",
                "собрать apk",
                "сборка приложения"
            ],
            "/register_group": [
                "зарегистрировать группу",
                "регистрация группы",
                "добавить группу",
                "зарегистрировать чат"
            ],
            "/users": [
                "пользователи",
                "список пользователей",
                "управление пользователями",
                "показать пользователей"
            ],
            "/groups": [
                "группы",
                "список групп",
                "показать группы",
                "зарегистрированные группы"
            ]
        }
        
        # Pre-compute embeddings for all command descriptions
        logger.info("Computing command embeddings...")
        self.command_embeddings = {}
        for cmd, descriptions in self.commands.items():
            embeddings = self.model.encode(descriptions, convert_to_tensor=True)
            self.command_embeddings[cmd] = embeddings
        
        logger.info(f"CommandMatcher initialized. Loaded {len(self.commands)} commands.")
    
    def match_command(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Find the most suitable command for the given text.
        
        Args:
            text: User message text
            
        Returns:
            Tuple (command, similarity level) or None if similarity is below threshold
        """
        if not text or not text.strip():
            return None
        
        # Clean text from bot mentions
        text = text.strip().lower()
        
        # Get user text embedding
        user_embedding = self.model.encode(text, convert_to_tensor=True)
        
        best_match = None
        best_score = 0.0
        
        # Compare with each command
        for cmd, cmd_embeddings in self.command_embeddings.items():
            # Calculate cosine similarity with all command descriptions
            similarities = util.cos_sim(user_embedding, cmd_embeddings)[0]
            
            # Take maximum similarity
            max_similarity = torch.max(similarities).item()
            
            if max_similarity > best_score:
                best_score = max_similarity
                best_match = cmd
        
        # Check if best match exceeds threshold
        if best_match and best_score >= self.threshold:
            logger.info(f"Match: '{text}' -> {best_match} (similarity: {best_score:.3f})")
            return best_match, best_score
        else:
            logger.debug(f"No match found for '{text}'. Best similarity: {best_score:.3f}")
            return None


# Global instance for lazy initialization
_matcher_instance: Optional[CommandMatcher] = None


def get_command_matcher() -> CommandMatcher:
    """
    Get global CommandMatcher instance (lazy initialization).
    
    Returns:
        Initialized CommandMatcher
    """
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = CommandMatcher()
    return _matcher_instance

