import configparser
from pathlib import Path
from typing import Any, Dict

class ConfigService:
    """
    Service for loading and parsing the config.ini file.
    """

    def load_config(self, path: Path) -> Dict[str, Any]:
        """
        Loads configuration from the given .ini file path.

        Args:
            path: The path to the configuration file.

        Returns:
            A dictionary containing the settings.
        """
        parser = configparser.ConfigParser()
        # According to configparser docs, reading a non-existent file
        # results in an empty dataset, which is safe.
        parser.read(path)

        settings: Dict[str, Any] = {}
        if "defaults" not in parser:
            return settings

        defaults = parser["defaults"]

        # We need to handle type conversion explicitly
        if "output_path" in defaults:
            settings["output_path"] = defaults["output_path"]
        if "min_likes" in defaults:
            settings["min_likes"] = defaults.getint("min_likes")
        if "min_views" in defaults:
            settings["min_views"] = defaults.getint("min_views")
        if "transcripts" in defaults:
            settings["transcripts"] = defaults.getboolean("transcripts")

        return settings
