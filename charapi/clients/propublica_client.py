import requests
import yaml
from typing import List, Dict, Optional
from ..data.mock_data import MOCK_ORGANIZATION_DATA, MOCK_SEARCH_RESULTS
from ..cache.api_cache import APICache


class ProPublicaClient:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self.base_url = config["propublica"]["base_url"]
        self.timeout = config["propublica"]["timeout"]

        global_mock = config.get("mock_mode", False)
        service_mock = config["propublica"].get("mock_mode", False)
        self.mock_mode = global_mock or service_mock

        # Initialize caching
        cache_config = config.get("caching", {})
        self.cache_enabled = cache_config.get("enabled", False) and not self.mock_mode

        if self.cache_enabled:
            self.cache = APICache(
                database_path=cache_config.get("database_path", "cache/charapi_cache.db"),
                default_ttl_hours=cache_config.get("default_ttl_hours", 24)
            )
            self.propublica_ttl = cache_config.get("propublica_ttl_hours", 24)

            if cache_config.get("cleanup_on_startup", False):
                self.cache.cleanup_expired()
    
    def search_organizations(self, query: str) -> List[Dict]:
        if self.mock_mode:
            return self._mock_search(query)

        # Check cache first
        if self.cache_enabled:
            cached_result = self.cache.get("propublica", "search", query)
            if cached_result is not None:
                return cached_result

        url = f"{self.base_url}/search.json"
        response = requests.get(url, params={"q": query}, timeout=self.timeout)
        response.raise_for_status()
        result = response.json().get("organizations", [])

        # Cache the result
        if self.cache_enabled:
            self.cache.set("propublica", "search", query, result, self.propublica_ttl)

        return result
    
    def get_organization(self, ein: str) -> Dict:
        if self.mock_mode:
            return self._mock_organization(ein)

        # Check cache first
        if self.cache_enabled:
            cached_result = self.cache.get("propublica", "organization", ein)
            if cached_result is not None:
                return cached_result

        url = f"{self.base_url}/organizations/{ein}.json"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()

        # Cache the result
        if self.cache_enabled:
            self.cache.set("propublica", "organization", ein, result, self.propublica_ttl)

        return result
    
    def get_all_filings(self, ein: str) -> List[Dict]:
        if self.mock_mode:
            return self._mock_filings(ein)

        # Check cache first
        if self.cache_enabled:
            cached_result = self.cache.get("propublica", "filings", ein)
            if cached_result is not None:
                return cached_result

        org_data = self.get_organization(ein)
        # Real API uses filings_with_data instead of filings
        result = org_data.get("filings_with_data", [])

        # Cache the result
        if self.cache_enabled:
            self.cache.set("propublica", "filings", ein, result, self.propublica_ttl)

        return result

    def get_cache_stats(self) -> dict:
        if self.cache_enabled:
            return self.cache.get_stats()
        return {"cache_enabled": False}

    def clear_cache(self):
        if self.cache_enabled:
            self.cache.clear_all()

    def _mock_search(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        for search_term, results in MOCK_SEARCH_RESULTS.items():
            if search_term in query_lower:
                return results
        return []
    
    def _mock_organization(self, ein: str) -> Dict:
        if ein in MOCK_ORGANIZATION_DATA:
            return MOCK_ORGANIZATION_DATA[ein]
        return {"name": f"Mock Organization {ein}", "ein": ein, "filings": []}
    
    def _mock_filings(self, ein: str) -> List[Dict]:
        if ein in MOCK_ORGANIZATION_DATA:
            return MOCK_ORGANIZATION_DATA[ein]["filings"]
        return []