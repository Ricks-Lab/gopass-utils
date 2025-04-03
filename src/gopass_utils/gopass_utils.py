"""
Gopass Utils

A set of utilities to manage secrets with Gopass and extract them as needed.
Provides support for environment-based scoping, caching, and optional JSON decoding.
"""

import subprocess
import json
import logging
from typing import Optional

class Gopass:
    def __init__(self, environment: Optional[str] = None, cache_enabled: bool = True, logger: Optional[logging.Logger] = None):
        self.env = environment.strip('/') if environment else None
        self.cache_enabled = cache_enabled
        self._cache = {} if cache_enabled else None
        self.logger = logger or logging.getLogger(__name__)

    def _build_path(self, path: str) -> str:
        return f"{self.env}/{path}" if self.env else path

    def get_secret(self, path: str) -> str:
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
        raw = self.get_secret(path)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse secret at '%s' as JSON", path)
            raise ValueError(f"Secret at '{path}' is not valid JSON")

    def clear_cache(self):
        if self.cache_enabled:
            self._cache.clear()
            self.logger.debug("[Gopass] Cache cleared")

