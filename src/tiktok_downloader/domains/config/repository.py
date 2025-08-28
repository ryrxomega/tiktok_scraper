"""
Repository for handling configuration data access.
"""
import configparser
from pathlib import Path
from typing import Dict, Any, Callable

from .schemas import Config


class ConfigRepository:
    """
    A repository for loading application configuration from a file.

    This class abstracts the details of file I/O and parsing, providing
    a clean interface for retrieving configuration settings.
    """

    def load_from_path(self, path: Path) -> Config:
        """
        Loads and parses an INI file into a Config object.

        If the file or the 'defaults' section does not exist, it will
        return a Config object with default (None) values.

        Args:
            path: The Path object pointing to the .ini configuration file.

        Returns:
            A Pydantic Config model instance populated with the settings.
        """
        parser = configparser.ConfigParser()
        parser.read(path)

        if "defaults" not in parser:
            return Config()

        defaults = parser["defaults"]
        settings: Dict[str, Any] = {}

        # Map setting names to the appropriate ConfigParser 'get' method
        setting_getters: Dict[str, Callable[..., Any]] = {
            "output_path": defaults.get,
            "min_likes": defaults.getint,
            "min_views": defaults.getint,
            "transcripts": defaults.getboolean,
            "transcript_language": defaults.get,
            "concurrent_downloads": defaults.getint,
            "min_sleep_interval": defaults.getint,
            "max_sleep_interval": defaults.getint,
            "cookies_from_browser": defaults.get,
            "cookies_file": defaults.get
        }

        for setting, getter in setting_getters.items():
            if setting in defaults:
                settings[setting] = getter(setting)

        return Config(**settings)
