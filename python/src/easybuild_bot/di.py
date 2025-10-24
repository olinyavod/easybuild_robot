"""
Dependency Injection container for EasyBuild Bot.

Uses dependency_injector library for managing dependencies.
"""
from dependency_injector import containers, providers
from .storage import Storage
from .command_matcher import CommandMatcher


class Container(containers.DeclarativeContainer):
    """DI Container for application dependencies."""
    
    # Configuration
    config = providers.Configuration()
    
    # Database storage
    storage = providers.Singleton(
        Storage,
        dir_path=config.database.dir_path,
        db_name=config.database.db_name,
    )
    
    # Command matcher
    command_matcher = providers.Singleton(
        CommandMatcher,
        model_name=config.command_matcher.model_name,
        threshold=config.command_matcher.threshold,
    )

