import requests
from typing import List, Dict
from .base_client import BaseAPIClient
from ..data.mock_data import MOCK_ORGANIZATION_DATA, MOCK_SEARCH_RESULTS


class ProPublicaClient(BaseAPIClient):
    def __init__(self, config_path: str):
        super().__init__(config_path, "propublica")
        self.base_url = self.service_config["base_url"]
        self.timeout = self.service_config["timeout"]
    
    def search_organizations(self, query: str) -> List[Dict]:
        def fetch():
            url = f"{self.base_url}/search.json"
            response = requests.get(url, params={"q": query}, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("organizations", [])

        return self.get_cached_or_fetch(
            "search",
            query,
            fetch,
            lambda: self._mock_search(query)
        )
    
    def get_organization(self, ein: str) -> Dict:
        def fetch():
            url = f"{self.base_url}/organizations/{ein}.json"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        return self.get_cached_or_fetch(
            "organization",
            ein,
            fetch,
            lambda: self._mock_organization(ein)
        )
    
    def get_all_filings(self, ein: str) -> List[Dict]:
        def fetch():
            org_data = self.get_organization(ein)
            return org_data.get("filings_with_data", [])

        return self.get_cached_or_fetch(
            "filings",
            ein,
            fetch,
            lambda: self._mock_filings(ein)
        )

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