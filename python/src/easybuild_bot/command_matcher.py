"""
Модуль для семантического сопоставления пользовательских сообщений с командами бота
с использованием модели ruBert-tiny от Сбербанка.
"""
import logging
from typing import Optional, Tuple
from sentence_transformers import SentenceTransformer, util
import torch

logger = logging.getLogger(__name__)


class CommandMatcher:
    """Класс для семантического сопоставления текста с командами бота."""
    
    def __init__(self, model_name: str = "cointegrated/rubert-tiny", threshold: float = 0.5):
        """
        Инициализация модели для сопоставления команд.
        
        Args:
            model_name: Название модели из HuggingFace
            threshold: Порог схожести для определения совпадения (0.0-1.0)
        """
        logger.info(f"Загрузка модели {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold
        
        # Определяем команды и их описания на русском языке
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
        
        # Предварительно вычисляем эмбеддинги для всех описаний команд
        logger.info("Вычисление эмбеддингов команд...")
        self.command_embeddings = {}
        for cmd, descriptions in self.commands.items():
            embeddings = self.model.encode(descriptions, convert_to_tensor=True)
            self.command_embeddings[cmd] = embeddings
        
        logger.info(f"CommandMatcher инициализирован. Загружено {len(self.commands)} команд.")
    
    def match_command(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Находит наиболее подходящую команду для данного текста.
        
        Args:
            text: Текст сообщения пользователя
            
        Returns:
            Кортеж (команда, уровень схожести) или None, если схожесть ниже порога
        """
        if not text or not text.strip():
            return None
        
        # Очищаем текст от упоминаний бота
        text = text.strip().lower()
        
        # Получаем эмбеддинг текста пользователя
        user_embedding = self.model.encode(text, convert_to_tensor=True)
        
        best_match = None
        best_score = 0.0
        
        # Сравниваем с каждой командой
        for cmd, cmd_embeddings in self.command_embeddings.items():
            # Вычисляем косинусное сходство со всеми описаниями команды
            similarities = util.cos_sim(user_embedding, cmd_embeddings)[0]
            
            # Берем максимальное сходство
            max_similarity = torch.max(similarities).item()
            
            if max_similarity > best_score:
                best_score = max_similarity
                best_match = cmd
        
        # Проверяем, превышает ли лучшее совпадение порог
        if best_match and best_score >= self.threshold:
            logger.info(f"Сопоставление: '{text}' -> {best_match} (схожесть: {best_score:.3f})")
            return best_match, best_score
        else:
            logger.debug(f"Совпадение не найдено для '{text}'. Лучшая схожесть: {best_score:.3f}")
            return None


# Глобальный экземпляр для ленивой инициализации
_matcher_instance: Optional[CommandMatcher] = None


def get_command_matcher() -> CommandMatcher:
    """
    Получить глобальный экземпляр CommandMatcher (ленивая инициализация).
    
    Returns:
        Инициализированный CommandMatcher
    """
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = CommandMatcher()
    return _matcher_instance

