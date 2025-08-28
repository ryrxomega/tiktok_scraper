"""
Service layer for the configuration domain.
"""
from pathlib import Path

from .repository import ConfigRepository
from .schemas import Config


class ConfigService:
    """
    Orchestrates the loading of application configuration.

    This service acts as a go-between for the application's entry points
    (like the CLI) and the data access layer (the repository).
    """

    def __init__(self, repository: ConfigRepository):
        """
        Initializes the service with a repository instance.

        Args:
            repository: An instance of ConfigRepository to handle data access.
        """
        self._repository = repository

    def load_config(self, path: Path) -> Config:
        """
        Loads configuration from a given path using the repository.

        Args:
            path: The path to the configuration file.

        Returns:
            A Config object containing the application settings.
        """
        return self._repository.load_from_path(path)
