import yaml
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from ..cache.api_cache import APICache


class BaseAPIClient:
    def __init__(self, config_path: str, service_name: str):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.config_path = config_path
        self.service_name = service_name
        self.service_config = self.config[service_name]

        self._initialize_mock_mode()
        self._initialize_cache()

    def _initialize_mock_mode(self):
        global_mock = self.config.get("mock_mode", False)
        service_mock = self.service_config.get("mock_mode", False)
        self.mock_mode = global_mock or service_mock

    def _initialize_cache(self):
        cache_config = self.config.get("caching", {})
        self.cache_enabled = cache_config.get("enabled", False) and not self.mock_mode

        if self.cache_enabled:
            database_path_str = cache_config.get("database_path", "cache/charapi_cache.db")
            database_path = self._resolve_path(database_path_str)

            self.cache = APICache(
                database_path=str(database_path),
                default_ttl_hours=cache_config.get("default_ttl_hours", 24)
            )
            self.service_ttl = cache_config.get(f"{self.service_name}_ttl_hours", 24)

            if cache_config.get("cleanup_on_startup", False):
                self.cache.cleanup_expired()

    def _resolve_path(self, path_str: str) -> Path:
        path = Path(path_str)
        if path.is_absolute():
            return path

        config_file_path = Path(self.config_path).resolve()
        project_root = self._find_project_root(config_file_path)
        return project_root / path

    def _find_project_root(self, start_path: Path) -> Path:
        current = start_path.parent
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                return current
            current = current.parent
        return start_path.parent

    def get_cached_or_fetch(
        self,
        endpoint: str,
        identifier: str,
        fetch_function: Callable[[], Any],
        mock_function: Optional[Callable[[], Any]]
    ) -> Any:
        if self.mock_mode and mock_function:
            return mock_function()

        if self.cache_enabled:
            cached_result = self.cache.get(self.service_name, endpoint, identifier)
            if cached_result is not None:
                return cached_result

        result = fetch_function()

        if self.cache_enabled:
            self.cache.set(self.service_name, endpoint, identifier, result, self.service_ttl)

        return result

    def get_cache_stats(self) -> Dict[str, Any]:
        if self.cache_enabled:
            return self.cache.get_stats()
        return {"cache_enabled": False}

    def clear_cache(self):
        if self.cache_enabled:
            self.cache.clear_all()