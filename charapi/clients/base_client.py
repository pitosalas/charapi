import yaml
from typing import Optional, Dict, Any, Callable
from ..cache.api_cache import APICache


class BaseAPIClient:
    def __init__(self, config_path: str, service_name: str):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

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
            self.cache = APICache(
                database_path=cache_config.get("database_path", "cache/charapi_cache.db"),
                default_ttl_hours=cache_config.get("default_ttl_hours", 24)
            )
            self.service_ttl = cache_config.get(f"{self.service_name}_ttl_hours", 24)

            if cache_config.get("cleanup_on_startup", False):
                self.cache.cleanup_expired()

    def get_cached_or_fetch(
        self,
        endpoint: str,
        identifier: str,
        fetch_function: Callable[[], Any],
        mock_function: Optional[Callable[[], Any]] = None
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