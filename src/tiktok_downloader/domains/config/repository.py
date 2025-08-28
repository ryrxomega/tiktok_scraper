"""
Repository for handling configuration data access.
"""
import configparser
from pathlib import Path
from typing import Dict, Any

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

        settings: Dict[str, Any] = {}
        if "defaults" in parser:
            defaults = parser["defaults"]
            # The .get* methods of ConfigParser handle type conversion.
            # We check for presence before getting to avoid errors.
            if "output_path" in defaults:
                settings["output_path"] = defaults.get("output_path")
            if "min_likes" in defaults:
                settings["min_likes"] = defaults.getint("min_likes")
            if "min_views" in defaults:
                settings["min_views"] = defaults.getint("min_views")
            if "transcripts" in defaults:
                settings["transcripts"] = defaults.getboolean("transcripts")
            if "transcript_language" in defaults:
                settings["transcript_language"] = defaults.get("transcript_language")
            if "concurrent_downloads" in defaults:
                settings["concurrent_downloads"] = defaults.getint("concurrent_downloads")
            if "min_sleep_interval" in defaults:
                settings["min_sleep_interval"] = defaults.getint("min_sleep_interval")
            if "max_sleep_interval" in defaults:
                settings["max_sleep_interval"] = defaults.getint("max_sleep_interval")

        # Pydantic will validate the types upon instantiation.
        return Config(**settings)
