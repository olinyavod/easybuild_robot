"""
Dependency Injection container for EasyBuild Bot.

Uses dependency_injector library for managing dependencies.
"""
from dependency_injector import containers, providers
from .storage import Storage
from .access_control import AccessControlService
from .commands import create_command_system


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
    
    # Access control service
    access_control = providers.Singleton(
        AccessControlService,
        storage=storage,
    )
    
    # Command Pattern system
    command_system = providers.Singleton(
        create_command_system,
        storage=storage,
        access_control=access_control,
        model_name=config.command_matcher.model_name,
        threshold=config.command_matcher.threshold,
    )
    
    # Extract registry and executor from command_system tuple
    command_registry = providers.Callable(
        lambda system: system[0],
        system=command_system
    )
    
    command_executor = providers.Callable(
        lambda system: system[1],
        system=command_system
    )
