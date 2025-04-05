"""
Gopass Utils

A set of utilities to manage secrets with Gopass and extract them as needed.
Provides support for environment-based scoping, caching, and optional JSON decoding.
"""

__docformat__ = 'reStructuredText'

import subprocess
import json
import logging
from typing import Optional

class Gopass:
    """
    Gopass interface for retrieving secrets securely using the gopass CLI.

    :param environment: Prefix path to apply to all secrets (e.g., "prod").
    :type environment: str, optional
    :param cache_enabled: If True, secrets will be cached in-memory after retrieval.
    :type cache_enabled: bool
    :param logger: Custom logger instance to use. Defaults to module logger.
    :type logger: logging.Logger, optional
    """

    def __init__(self, environment: Optional[str] = None, cache_enabled: bool = True, logger: Optional[logging.Logger] = None):
        self.env = environment.strip('/') if environment else None
        self.cache_enabled = cache_enabled
        self._cache = {} if cache_enabled else None
        self.logger = logger or logging.getLogger(__name__)

    def _build_path(self, path: str) -> str:
        """
        Build the full secret path using the optional environment prefix.

        :param path: Secret path relative to the environment.
        :type path: str
        :return: Full secret path.
        :rtype: str
        """
        return f"{self.env}/{path}" if self.env else path

    def get_secret(self, path: str) -> str:
        """
        Retrieve a secret from gopass.

        :param path: Path to the secret in the gopass store.
        :type path: str
        :return: The decrypted secret value.
        :rtype: str
        :raises RuntimeError: If gopass fails to retrieve the secret.
        """
        full_path = self._build_path(path)

        if self.cache_enabled and full_path in self._cache:
            self.logger.debug("[Gopass] Returning cached secret for: %s", full_path)
            return self._cache[full_path]

        try:
            result = subprocess.run(
                ["gopass", "show", "-o", full_path],
                capture_output=True,
                text=True,
                check=True
            )
            secret = result.stdout.strip()
            if self.cache_enabled:
                self._cache[full_path] = secret
            return secret
        except subprocess.CalledProcessError as e:
            self.logger.error("Gopass failed for '%s': %s", full_path, e.stderr.strip())
            raise RuntimeError(f"Gopass failed for '{full_path}': {e.stderr.strip()}")

    def get_secret_json(self, path: str) -> dict:
        """
        Retrieve and parse a secret as a JSON object.

        Assumes the secret content is a valid JSON string.

        :param path: Path to the secret.
        :type path: str
        :return: Parsed JSON object.
        :rtype: dict
        :raises ValueError: If the secret content is not valid JSON.
        """
        raw = self.get_secret(path)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse secret at '%s' as JSON", path)
            raise ValueError(f"Secret at '{path}' is not valid JSON")

    def clear_cache(self):
        """
        Clear the internal in-memory secret cache.
        """
        if self.cache_enabled:
            self._cache.clear()
            self.logger.debug("[Gopass] Cache cleared")
