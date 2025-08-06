import yaml
import os

class Config:
    def __init__(self, config_file="../../configs/config.yaml"):
        """
        Initialize the Config object and load the YAML configuration file.

        Args:
            config_file (str): Path to the YAML configuration file.
        """
        self._config_file = os.path.abspath(config_file)  # Convert to an absolute path
        self._config = None
        self._load_config()

    def _load_config(self):
        """Load the configuration file into memory."""
        if not os.path.exists(self._config_file):
            raise FileNotFoundError(f"Config file not found: {self._config_file}")
        
        with open(self._config_file, "r") as file:
            self._config = yaml.safe_load(file)

    def get(self, key, default=None):
        """
        Retrieve a value from the configuration file.

        Args:
            key (str): Dot-separated key (e.g., 'data_path.elec.processed.folder').
            default: The default value to return if the key is not found.

        Returns:
            The value from the config or the default if key is not found.
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if not isinstance(value, dict):  # Ensure value is a dictionary before diving deeper
                return default
            value = value.get(k, default)
        return value

    def get_path(self, key, **kwargs):
        """
        Retrieve and resolve a path from the configuration file.

        Args:
            key (str): Dot-separated key for the path (e.g., 'data_path.elec.processed.folder').
            kwargs: Dynamic variables to format the path (e.g., {year}, {month}, {cliente}).

        Returns:
            str: The resolved absolute path.

        Raises:
            KeyError: If the key is not found.
            TypeError: If the key does not contain a valid string.
        """
        value = self.get(key)

        if value is None:
            raise KeyError(f"Key '{key}' not found in configuration.")
        if not isinstance(value, str):
            raise TypeError(f"Key '{key}' does not contain a valid path string.")

        # Format placeholders in the path (if any)
        try:
            resolved_path = value.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"Missing dynamic variable for placeholder: {str(e)}")

        # Return as an absolute path
        return os.path.abspath(resolved_path)


    def get_resolved_path(self, key, **kwargs):
        """
        Retrieve and validate a path, ensuring it exists.

        Args:
            key (str): Dot-separated key for the path.
            kwargs: Dynamic variables to format the path.

        Returns:
            str: The resolved absolute path.

        Raises:
            FileNotFoundError: If the resolved path does not exist.
        """
        resolved_path = self.get_path(key, **kwargs)
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"Resolved path does not exist: {resolved_path}")
        return resolved_path
